import ipaddress
import json
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from connectors.core.connector import ConnectorError
from pydantic import Field, ValidationError, field_validator, model_validator

from ...constants import INTHREAT_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class AddToIocCollectionParams(InputModel):
    ioc_collection_id: str
    indicator_type: Literal["IP address", "domain", "url", "email", "hash"]
    indicator: Optional[str] = None
    indicators: Optional[list[str]] = None
    valid_for: Optional[int] = Field(default=None, ge=1)

    @field_validator("indicators", mode="before")
    @classmethod
    def parse_indicators(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError("Expected a JSON array for indicators.") from e
            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON array for indicators.")
            return [str(item) for item in parsed]
        raise ValueError("Expected a JSON array for indicators.")

    @model_validator(mode="after")
    def validate_indicator_input(self):
        has_single = self.indicator is not None and self.indicator != ""
        has_list = self.indicators is not None and len(self.indicators) > 0

        if not has_single and not has_list:
            raise ValueError("Either indicator or indicators is required.")

        return self


class AddToIocCollectionOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = AddToIocCollectionParams

    def build_endpoint(self, parsed_input: AddToIocCollectionParams) -> str:
        return (
            f"{INTHREAT_V2_BASE_URL}/ioc-collections/"
            f"{parsed_input.ioc_collection_id}/indicators/text"
        )

    def _resolve_indicators(self, parsed_input: AddToIocCollectionParams) -> list[str]:
        if parsed_input.indicators is not None and len(parsed_input.indicators) > 0:
            return [str(item) for item in parsed_input.indicators]
        return [str(parsed_input.indicator)]

    @staticmethod
    def _valid_until(valid_for: Optional[int]) -> Optional[str]:
        if not valid_for:
            return None
        return (datetime.now(timezone.utc) + timedelta(days=valid_for)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    @staticmethod
    def _format_for_non_ip(indicator_type: str) -> str:
        mapping = {
            "domain": "domain-name.value",
            "url": "url.value",
            "email": "email-addr.value",
            "hash": "file.hashes",
        }
        return mapping[indicator_type]

    def _build_text_payload(
        self,
        indicators: list[str],
        indicator_format: str,
        valid_for: Optional[int],
    ) -> dict:
        payload = {
            "format": indicator_format,
            "indicators": "\n".join(indicators),
        }
        valid_until = self._valid_until(valid_for)
        if valid_until:
            payload["valid_until"] = valid_until
        return payload

    def build_payload(self, parsed_input: AddToIocCollectionParams) -> dict:
        indicators = self._resolve_indicators(parsed_input)
        indicator_format = self._format_for_non_ip(parsed_input.indicator_type)
        return self._build_text_payload(
            indicators,
            indicator_format,
            parsed_input.valid_for,
        )

    def perform(self, config: dict, parsed_input: AddToIocCollectionParams):
        endpoint = self.build_endpoint(parsed_input)
        indicators = self._resolve_indicators(parsed_input)

        try:
            if parsed_input.indicator_type != "IP address":
                payload = self.build_payload(parsed_input)
                return self.api_action_cls(config, "POST", endpoint, json=payload).run()

            ipv4: list[str] = []
            ipv6: list[str] = []
            invalid: list[str] = []
            for raw in indicators:
                value = str(raw).strip()
                if not value:
                    invalid.append(str(raw))
                    continue
                try:
                    parsed_ip = ipaddress.ip_address(value)
                    if isinstance(parsed_ip, ipaddress.IPv4Address):
                        ipv4.append(value)
                    else:
                        ipv6.append(value)
                except ValueError:
                    invalid.append(value)

            if invalid:
                raise ConnectorError(
                    "Invalid IP indicator(s): "
                    + ", ".join(invalid)
                    + ". Expected plain IPv4/IPv6 addresses (CIDR notation is not supported)."
                )
            if not ipv4 and not ipv6:
                raise ConnectorError("No valid IP indicators were provided")

            responses = []
            if ipv4:
                payload = self._build_text_payload(
                    ipv4,
                    "ipv4-addr.value",
                    parsed_input.valid_for,
                )
                responses.append(
                    self.api_action_cls(config, "POST", endpoint, json=payload).run()
                )
            if ipv6:
                payload = self._build_text_payload(
                    ipv6,
                    "ipv6-addr.value",
                    parsed_input.valid_for,
                )
                responses.append(
                    self.api_action_cls(config, "POST", endpoint, json=payload).run()
                )

            if len(responses) == 1:
                return responses[0]
            return {"results": responses}
        except ValidationError as e:
            raise ConnectorError(f"Error: Invalid parameters: {e}") from e
        except Exception as e:
            if isinstance(e, ConnectorError):
                raise
            raise ConnectorError(f"Error: {e}") from e


def add_to_ioc_collection(config, params: dict):
    """Add one or many indicators to an IOC collection."""
    return AddToIocCollectionOperation(api_action_cls=GenericAPIAction).execute(
        config,
        params,
    )
