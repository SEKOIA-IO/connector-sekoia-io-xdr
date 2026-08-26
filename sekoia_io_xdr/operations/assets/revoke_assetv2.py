from ...constants import ASSETS_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class RevokeAssetV2Params(InputModel):
    uuid: str


class RevokeAssetV2Operation(Operation):
    http_method = "PUT"
    payload_parameter = None
    input_model = RevokeAssetV2Params

    def build_endpoint(self, parsed_input: RevokeAssetV2Params) -> str:
        return f"{ASSETS_V2_BASE_URL}/{parsed_input.uuid}/revoke"

    def build_payload(self, parsed_input: RevokeAssetV2Params):
        return None


def revoke_assetv2(config, params):
    """Revoke an asset (v2)."""
    return RevokeAssetV2Operation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
