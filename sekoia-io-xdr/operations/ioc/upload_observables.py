import json
from pathlib import Path
from typing import Any, Optional

from connectors.core.connector import ConnectorError
from pydantic import field_validator, model_validator

from ...constants import INTHREAT_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class UploadObservablesParams(InputModel):
    observables: Optional[Any] = None
    observables_path: Optional[str] = None

    @field_validator("observables", mode="before")
    @classmethod
    def parse_observables(cls, value):
        if value is None:
            return None
        if isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                return json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "Expected observables to be a JSON array or object."
                ) from e
        raise ValueError("Expected observables to be a JSON array or object.")

    @model_validator(mode="after")
    def validate_input(self):
        has_observables = self.observables is not None
        has_path = self.observables_path is not None and self.observables_path != ""
        if not has_observables and not has_path:
            raise ValueError("Either observables or observables_path is required.")
        return self


class UploadObservablesOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = UploadObservablesParams

    def build_endpoint(self, parsed_input: UploadObservablesParams) -> str:
        return f"{INTHREAT_V2_BASE_URL}/observables/bulk"

    def _load_observables_from_path(self, path_value: str) -> Any:
        path = Path(path_value)
        try:
            with path.open(encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise ConnectorError(f"Observables file not found: {path_value}") from e
        except json.JSONDecodeError as e:
            raise ConnectorError(
                f"Observables file is not valid JSON: {path_value}"
            ) from e

    def build_payload(self, parsed_input: UploadObservablesParams) -> dict:
        observables = parsed_input.observables
        if observables is None:
            observables = self._load_observables_from_path(
                parsed_input.observables_path
            )
        return {"data": observables}


def upload_observables(config, params: dict):
    """Upload observables to inThreat bulk endpoint."""
    return UploadObservablesOperation(api_action_cls=GenericAPIAction).execute(
        config,
        params,
    )
