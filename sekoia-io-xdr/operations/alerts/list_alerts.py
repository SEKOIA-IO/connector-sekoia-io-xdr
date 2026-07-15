from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class ListAlertsParams(InputModel):
    pass


class ListAlertsOperation(Operation):
    http_method = "get"
    payload_parameter = "params"
    input_model = ListAlertsParams

    # Single source of truth for deprecated aliases used in payload fallback.
    deprecated_aliases = DeprecatedAliases(
        single={
            "match[short_id]": "short_id",
            "match[rule_name]": "rule_name",
            "match[rule_uuid]": "rule_uuid",
            "match[status_name]": "status_name",
            "match[status_uuid]": "status_uuid",
        },
        range={
            "date[created_at]": ("creation_start_date", "creation_end_date"),
            "date[updated_at]": ("updated_start_date", "updated_end_date"),
        },
    )

    def build_endpoint(self, parsed_input: ListAlertsParams) -> str:
        return ALERTS_V1_BASE_URL

    def build_payload(self, parsed_input: ListAlertsParams) -> dict:
        params = parsed_input.model_dump()

        return {
            "cases": self.payload_value(params, "cases", default=False),
            "date[created_at]": self.payload_value(
                params,
                "date[created_at]",
            ),
            "date[updated_at]": self.payload_value(
                params,
                "date[updated_at]",
            ),
            "direction": self.payload_value(params, "direction"),
            "is_assigned_to_case": self.payload_value(params, "is_assigned_to_case"),
            "limit": self.payload_value(params, "limit", default=20),
            "match[asset_uuid]": self.payload_value(params, "match[asset_uuid]"),
            "match[assignee]": self.payload_value(params, "match[assignee]"),
            "match[case_short_id]": self.payload_value(params, "match[case_short_id]"),
            "match[community_uuid]": self.payload_value(
                params, "match[community_uuid]"
            ),
            "match[custom_status_uuid]": self.payload_value(
                params, "match[custom_status_uuid]"
            ),
            "match[detection_type]": self.payload_value(
                params, "match[detection_type]"
            ),
            "match[entity_name]": self.payload_value(params, "match[entity_name]"),
            "match[entity_uuid]": self.payload_value(params, "match[entity_uuid]"),
            "match[node]": self.payload_value(params, "match[node]"),
            "match[rule_name]": self.payload_value(
                params,
                "match[rule_name]",
            ),
            "match[rule_uuid]": self.payload_value(
                params,
                "match[rule_uuid]",
            ),
            "match[short_id]": self.payload_value(
                params,
                "match[short_id]",
            ),
            "match[source]": self.payload_value(params, "match[source]"),
            "match[status_name]": self.payload_value(
                params,
                "match[status_name]",
            ),
            "match[status_uuid]": self.payload_value(
                params,
                "match[status_uuid]",
            ),
            "match[stix_object]": self.payload_value(params, "match[stix_object]"),
            "match[target]": self.payload_value(params, "match[target]"),
            "match[title]": self.payload_value(params, "match[title]"),
            "match[type_category]": self.payload_value(params, "match[type_category]"),
            "match[type_value]": self.payload_value(params, "match[type_value]"),
            "match[urgency_display]": self.payload_value(
                params, "match[urgency_display]"
            ),
            "match[uuid]": self.payload_value(params, "match[uuid]"),
            "match[verdict_uuid]": self.payload_value(params, "match[verdict_uuid]"),
            "nomatch[asset_uuid]": self.payload_value(params, "nomatch[asset_uuid]"),
            "nomatch[assignee]": self.payload_value(params, "nomatch[assignee]"),
            "nomatch[custom_status_uuid]": self.payload_value(
                params, "nomatch[custom_status_uuid]"
            ),
            "nomatch[detection_type]": self.payload_value(
                params, "nomatch[detection_type]"
            ),
            "nomatch[entity_uuid]": self.payload_value(params, "nomatch[entity_uuid]"),
            "nomatch[rule_name]": self.payload_value(params, "nomatch[rule_name]"),
            "nomatch[rule_uuid]": self.payload_value(params, "nomatch[rule_uuid]"),
            "nomatch[source]": self.payload_value(params, "nomatch[source]"),
            "nomatch[status_uuid]": self.payload_value(params, "nomatch[status_uuid]"),
            "nomatch[stix_object]": self.payload_value(params, "nomatch[stix_object]"),
            "nomatch[target]": self.payload_value(params, "nomatch[target]"),
            "nomatch[type_value]": self.payload_value(params, "nomatch[type_value]"),
            "nomatch[urgency_display]": self.payload_value(
                params, "nomatch[urgency_display]"
            ),
            "nomatch[verdict_uuid]": self.payload_value(
                params, "nomatch[verdict_uuid]"
            ),
            "offset": self.payload_value(params, "offset", default=0),
            "range[similar]": self.payload_value(params, "range[similar]"),
            "range[urgency]": self.payload_value(params, "range[urgency]"),
            "similar_to": self.payload_value(params, "similar_to"),
            "sort": self.payload_value(params, "sort"),
            "stix": self.payload_value(params, "stix", default=False),
            "visible": self.payload_value(params, "visible", default=True),
            "with_count": self.payload_value(params, "with_count", default=True),
        }


def list_alerts(config, params):
    return ListAlertsOperation(api_action_cls=GenericAPIAction).execute(config, params)
