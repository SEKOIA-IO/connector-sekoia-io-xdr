import json
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator

from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CountermeasureComment(BaseModel):
    content: str
    author: Optional[str] = None


class DenyCountermeasureParams(InputModel):
    cm_uuid: str = Field(
        validation_alias=AliasChoices("cm_uuid", "countermeasure_uuid")
    )
    comment: Optional[CountermeasureComment] = None
    content: Optional[str] = None
    author: Optional[str] = None

    @field_validator("comment", mode="before")
    @classmethod
    def parse_comment(cls, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Expected a JSON object.")
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError("Expected a JSON object.") from e
            if not isinstance(parsed, dict):
                raise ValueError("Expected a JSON object.")
            return parsed
        raise ValueError("Expected a JSON object.")

    @model_validator(mode="after")
    def build_legacy_comment(self):
        if self.comment is None:
            if self.content is None:
                raise ValueError("Either comment or content is required.")
            self.comment = CountermeasureComment(
                content=self.content, author=self.author
            )
        return self


class DenyCountermeasureOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = DenyCountermeasureParams
    deprecated_parameters = {
        "countermeasure_uuid": "cm_uuid",
        "content": "comment",
        "author": "comment",
    }

    def build_endpoint(self, parsed_input: DenyCountermeasureParams) -> str:
        return f"{ALERTS_V1_BASE_URL}/countermeasures/{parsed_input.cm_uuid}/deny"

    def build_payload(self, parsed_input: DenyCountermeasureParams) -> dict:
        return {"comment": parsed_input.comment.model_dump(exclude_none=True)}


def deny_countermeasure(config, params):
    """Deny a countermeasure."""
    return DenyCountermeasureOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
