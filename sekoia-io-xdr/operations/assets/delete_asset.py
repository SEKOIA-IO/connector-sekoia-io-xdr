from ...constants import ASSETS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class DeleteAssetParams(InputModel):
    asset_uuid: str


class DeleteAssetOperation(Operation):
    http_method = "DELETE"
    payload_parameter = None
    input_model = DeleteAssetParams

    def build_endpoint(self, parsed_input: DeleteAssetParams) -> str:
        return f"{ASSETS_V1_BASE_URL}/{parsed_input.asset_uuid}"

    def build_payload(self, parsed_input: DeleteAssetParams):
        return None


def delete_asset(config, params):
    """Delete a specific asset."""
    return DeleteAssetOperation(api_action_cls=GenericAPIAction).execute(config, params)
