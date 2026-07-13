from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Type

from connectors.core.connector import ConnectorError, get_logger
from pydantic import BaseModel, ConfigDict, ValidationError

from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


class InputModel(BaseModel):
    """Generic input schema for operations."""

    model_config = ConfigDict(extra="allow")


@dataclass
class DeprecatedAliases:
    """Canonical-to-deprecated alias mappings used by operation inputs."""

    single: dict[str, str] = field(default_factory=dict)
    range: dict[str, tuple[str, str]] = field(default_factory=dict)


class Operation(ABC):
    """Generic operation handler with typed validation and standardized execution."""

    http_method: str = "GET"
    payload_parameter: str | None = "params"  # params | json | None
    input_model: Type[InputModel] = InputModel
    deprecated_aliases: DeprecatedAliases = DeprecatedAliases()
    deprecated_parameters: dict[str, str] = {}  # deprecated -> field_name

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        aliases = getattr(cls, "deprecated_aliases", DeprecatedAliases())
        cls.deprecated_aliases = DeprecatedAliases(
            single=dict(getattr(aliases, "single", {})),
            range=dict(getattr(aliases, "range", {})),
        )

        auto_mapped = cls._build_deprecated_parameters()
        explicit = getattr(cls, "deprecated_parameters", {}) or {}
        cls.deprecated_parameters = {**auto_mapped, **explicit}

    def __init__(self, api_action_cls: Type[GenericAPIAction] = GenericAPIAction):
        self.api_action_cls = api_action_cls

    @classmethod
    def _build_deprecated_parameters(cls) -> dict[str, str]:
        mapping: dict[str, str] = {}

        for field_name, deprecated in cls.deprecated_aliases.single.items():
            mapping[deprecated] = field_name

        for field_name, pair in cls.deprecated_aliases.range.items():
            start_name, end_name = pair
            mapping[start_name] = field_name
            mapping[end_name] = field_name

        return mapping

    @staticmethod
    def _has_value(value: Any) -> bool:
        return value is not None and value != ""

    @staticmethod
    def _coerce_missing(value: Any, treat_falsy_as_missing: bool) -> Any:
        if treat_falsy_as_missing and not value:
            return None
        return value

    def _resolve_deprecated_range_value(
        self,
        params: dict[str, Any],
        field_name: str,
    ) -> Any:
        pair = self.deprecated_aliases.range.get(field_name)
        if not pair:
            return None

        start_name, end_name = pair
        start_value = params.get(start_name)
        end_value = params.get(end_name)
        if self._has_value(start_value) or self._has_value(end_value):
            return f"{start_value or ''},{end_value or ''}"

        return None

    def _resolve_deprecated_single_value(
        self,
        params: dict[str, Any],
        field_name: str,
        treat_falsy_as_missing: bool,
    ) -> Any:
        deprecated = self.deprecated_aliases.single.get(field_name)
        if not deprecated:
            return None

        deprecated_value = self._coerce_missing(
            params.get(deprecated),
            treat_falsy_as_missing,
        )
        if self._has_value(deprecated_value):
            return deprecated_value

        return None

    def resolve_payload_value(
        self,
        params: dict[str, Any],
        field_name: str,
        default: Any = None,
        *,
        treat_falsy_as_missing: bool = False,
    ) -> Any:
        current = self._coerce_missing(
            params.get(field_name),
            treat_falsy_as_missing,
        )

        if self._has_value(current):
            return current

        range_value = self._resolve_deprecated_range_value(params, field_name)
        if self._has_value(range_value):
            return range_value

        single_value = self._resolve_deprecated_single_value(
            params,
            field_name,
            treat_falsy_as_missing,
        )
        if self._has_value(single_value):
            return single_value

        return default

    def payload_value(
        self,
        params: dict[str, Any],
        field_name: str,
        default: Any = None,
        *,
        treat_falsy_as_missing: bool = False,
    ) -> Any:
        """Small readability wrapper for payload builders in operations."""
        return self.resolve_payload_value(
            params,
            field_name,
            default=default,
            treat_falsy_as_missing=treat_falsy_as_missing,
        )

    def _warn_deprecated_parameters(self, raw_input: dict[str, Any]) -> None:
        for deprecated, field_name in self.deprecated_parameters.items():
            if deprecated in raw_input:
                logger.warning(
                    "Deprecated parameter '%s' used; prefer '%s'.",
                    deprecated,
                    field_name,
                )

    def parse_input(self, raw_input: dict[str, Any]) -> InputModel:
        self._warn_deprecated_parameters(raw_input)
        try:
            return self.input_model.model_validate(raw_input)
        except ValidationError as e:
            raise ConnectorError(f"Error: Invalid parameters: {e}") from e

    def execute(self, config: dict[str, Any], raw_input: dict[str, Any]) -> Any:
        parsed_input = self.parse_input(raw_input)
        return self.perform(config, parsed_input)

    def perform(self, config: dict[str, Any], parsed_input: InputModel) -> Any:
        endpoint = self.build_endpoint(parsed_input)
        payload = self.build_payload(parsed_input)

        request_kwargs: dict[str, Any] = {}
        if self.payload_parameter and payload is not None:
            request_kwargs[self.payload_parameter] = payload

        try:
            response = self.api_action_cls(
                config,
                self.http_method,
                endpoint,
                **request_kwargs,
            ).run()
        except Exception as e:
            raise ConnectorError(f"Error: {e}") from e

        return response

    @abstractmethod
    def build_endpoint(self, parsed_input: InputModel) -> str:
        """Build request endpoint from validated input."""

    @abstractmethod
    def build_payload(self, parsed_input: InputModel) -> dict[str, Any] | None:
        """Build request payload/query params from validated input."""
