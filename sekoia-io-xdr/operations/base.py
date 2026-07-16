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
        # Copy alias mappings per subclass to avoid mutable shared state.
        cls.deprecated_aliases = cls._normalize_deprecated_aliases(
            getattr(cls, "deprecated_aliases", DeprecatedAliases())
        )

        # Build warning map once: deprecated_name -> canonical_name.
        auto_mapped = cls._build_deprecated_parameters()
        explicit = getattr(cls, "deprecated_parameters", {}) or {}
        cls.deprecated_parameters = {**auto_mapped, **explicit}

    def __init__(self, api_action_cls: Type[GenericAPIAction] = GenericAPIAction):
        self.api_action_cls = api_action_cls

    @staticmethod
    def _normalize_deprecated_aliases(aliases: DeprecatedAliases) -> DeprecatedAliases:
        """Clone alias mappings to avoid sharing mutable defaults across subclasses."""
        return DeprecatedAliases(
            single=dict(getattr(aliases, "single", {})),
            range=dict(getattr(aliases, "range", {})),
        )

    @classmethod
    def _build_deprecated_parameters(cls) -> dict[str, str]:
        """Build deprecated->canonical mapping used for warning logs."""
        # Example: single={"uuid": "asset_uuid"} -> {"asset_uuid": "uuid"}
        single_mapping = {
            deprecated: field_name
            for field_name, deprecated in cls.deprecated_aliases.single.items()
        }
        # Example: range={"date[created_at]": ("creation_start_date", "creation_end_date")}
        range_mapping = {
            alias: field_name
            for field_name, (
                start_name,
                end_name,
            ) in cls.deprecated_aliases.range.items()
            for alias in (start_name, end_name)
        }
        return {**single_mapping, **range_mapping}

    @staticmethod
    def _has_value(value: Any) -> bool:
        return value is not None and value != ""

    @staticmethod
    def _coerce_missing(value: Any, treat_falsy_as_missing: bool) -> Any:
        if treat_falsy_as_missing and not value:
            return None
        return value

    def _resolve_range_alias(
        self,
        params: dict[str, Any],
        field_name: str,
    ) -> Any:
        # If canonical date-range is missing, rebuild it from legacy start/end fields.
        pair = self.deprecated_aliases.range.get(field_name)
        if not pair:
            return None

        start_name, end_name = pair
        start_value = params.get(start_name)
        end_value = params.get(end_name)
        if self._has_value(start_value) or self._has_value(end_value):
            return f"{start_value or ''},{end_value or ''}"

        return None

    def _resolve_single_alias(
        self,
        params: dict[str, Any],
        field_name: str,
        treat_falsy_as_missing: bool,
    ) -> Any:
        # Resolve old parameter name for a canonical field.
        # Example: field_name='uuid' with alias 'asset_uuid'.
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
        """Resolve canonical field value, then fallback to deprecated aliases."""
        # 1) Prefer canonical input when present.
        current = self._coerce_missing(
            params.get(field_name),
            treat_falsy_as_missing,
        )

        if self._has_value(current):
            return current

        # 2) Then try legacy range aliases (start/end -> "start,end").
        range_value = self._resolve_range_alias(params, field_name)
        if self._has_value(range_value):
            return range_value

        # 3) Finally try legacy single alias.
        single_value = self._resolve_single_alias(
            params,
            field_name,
            treat_falsy_as_missing,
        )
        if self._has_value(single_value):
            return single_value

        # 4) Fallback default used by operation payload builders.
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
        # Alias-aware helper used by most build_payload implementations.
        return self.resolve_payload_value(
            params,
            field_name,
            default=default,
            treat_falsy_as_missing=treat_falsy_as_missing,
        )

    def _warn_on_deprecated_inputs(self, raw_input: dict[str, Any]) -> None:
        """Emit warning logs when deprecated parameter names are used."""
        # Warning only: legacy inputs are still accepted when aliases are configured.
        for deprecated, field_name in self.deprecated_parameters.items():
            if deprecated in raw_input:
                logger.warning(
                    "Deprecated parameter '%s' used; prefer '%s'.",
                    deprecated,
                    field_name,
                )

    def parse_input(self, raw_input: dict[str, Any]) -> InputModel:
        # Validate user input against the operation-specific pydantic model.
        self._warn_on_deprecated_inputs(raw_input)
        try:
            return self.input_model.model_validate(raw_input)
        except ValidationError as e:
            raise ConnectorError(f"Error: Invalid parameters: {e}") from e

    def execute(self, config: dict[str, Any], raw_input: dict[str, Any]) -> Any:
        # Public execution entrypoint used by operation functions.
        parsed_input = self.parse_input(raw_input)
        return self.perform(config, parsed_input)

    def perform(self, config: dict[str, Any], parsed_input: InputModel) -> Any:
        # Build endpoint + payload, then forward request to the shared API action.
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
