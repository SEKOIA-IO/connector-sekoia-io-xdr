from typing import Optional

from connectors.core.connector import get_logger

from ...utils import BaseGetEvents
from ..base import InputModel, Operation

logger = get_logger("sekoia-io-xdr")


class GetEventsParams(InputModel):
    query: str
    earliest_time: str
    latest_time: str
    limit: int = 100


class GetEventsOperation(Operation):
    # Non-GenericAPIAction flow, custom perform implementation below.
    http_method = "GET"
    payload_parameter = None
    input_model = GetEventsParams

    def build_endpoint(self, parsed_input: GetEventsParams) -> str:
        return ""

    def build_payload(self, parsed_input: GetEventsParams):
        return None

    def perform(self, config: dict, parsed_input: GetEventsParams):
        base_get_events = BaseGetEvents(config)
        base_get_events.configure_http_session()

        event_search_job_uuid: str = base_get_events.trigger_event_search_job(
            query=parsed_input.query,
            earliest_time=parsed_input.earliest_time,
            latest_time=parsed_input.latest_time,
        )

        base_get_events.wait_for_search_job_execution(
            event_search_job_uuid=event_search_job_uuid
        )

        limit = max(1, min(int(parsed_input.limit), 100))

        response_events = base_get_events.http_session.get(
            f"{base_get_events.events_api_path}/search/jobs/{event_search_job_uuid}/events",
            params={"limit": limit, "offset": 0},
        )
        response_events.raise_for_status()
        response_content: dict = response_events.json()

        results: Optional[list] = response_content.get("items", [])
        return {"events": results}


def get_events(config, params: dict):
    return GetEventsOperation().execute(config, params)
