import json
from pathlib import Path
from typing import Any, Optional

from connectors.core.connector import ConnectorError
from pydantic import field_validator, model_validator

from ...constants import INTHREAT_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CreateContentProposalParams(InputModel):
    bundle: Optional[dict[str, Any]] = None
    bundle_path: Optional[str] = None
    auto_merge: bool = False
    enrich: bool = True
    name: Optional[str] = None
    assigned_to: Optional[str] = None

    @field_validator("bundle", mode="before")
    @classmethod
    def parse_bundle(cls, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError("Expected bundle to be a JSON object.") from e
            if not isinstance(parsed, dict):
                raise ValueError("Expected bundle to be a JSON object.")
            return parsed
        raise ValueError("Expected bundle to be a JSON object.")

    @model_validator(mode="after")
    def validate_input(self):
        has_bundle = self.bundle is not None
        has_path = self.bundle_path is not None and self.bundle_path != ""
        if not has_bundle and not has_path:
            raise ValueError("Either bundle or bundle_path is required.")
        return self


class CreateContentProposalOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = CreateContentProposalParams

    def build_endpoint(self, parsed_input: CreateContentProposalParams) -> str:
        return f"{INTHREAT_V2_BASE_URL}/bundles"

    def _load_bundle_from_path(self, path_value: str) -> dict[str, Any]:
        path = Path(path_value)
        try:
            with path.open(encoding="utf-8") as f:
                payload = json.load(f)
        except FileNotFoundError as e:
            raise ConnectorError(f"Bundle file not found: {path_value}") from e
        except json.JSONDecodeError as e:
            raise ConnectorError(f"Bundle file is not valid JSON: {path_value}") from e

        if not isinstance(payload, dict):
            raise ConnectorError("Bundle file must contain a JSON object.")
        return payload

    def build_payload(self, parsed_input: CreateContentProposalParams) -> dict:
        bundle = parsed_input.bundle
        if bundle is None:
            bundle_path = parsed_input.bundle_path
            if bundle_path is None:
                raise ConnectorError("Either bundle or bundle_path is required.")
            bundle = self._load_bundle_from_path(bundle_path)
        return {"data": bundle}

    def perform(
        self, config: dict[str, Any], parsed_input: CreateContentProposalParams
    ):
        endpoint = self.build_endpoint(parsed_input)
        payload = self.build_payload(parsed_input)
        query_params = {
            "auto_merge": parsed_input.auto_merge,
            "enrich": parsed_input.enrich,
            "name": parsed_input.name,
            "assigned_to": parsed_input.assigned_to,
        }
        filtered_params = {
            key: value for key, value in query_params.items() if value is not None
        }

        try:
            response = self.api_action_cls(
                config,
                self.http_method,
                endpoint,
                params=filtered_params,
                json=payload,
            ).run()
        except Exception as e:
            raise ConnectorError(f"Error: {e}") from e

        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response


def create_content_proposal(config, params: dict):
    """Create a new content proposal from a STIX bundle."""
    return CreateContentProposalOperation(api_action_cls=GenericAPIAction).execute(
        config,
        params,
    )
