from typing import Optional

from connectors.core.connector import get_logger

from ..utils import BaseGetEvents

logger = get_logger("sekoia-io-xdr")


def get_events(config, params: dict):
    base_get_events = BaseGetEvents(config)
    base_get_events.configure_http_session()

    event_search_job_uuid: str = base_get_events.trigger_event_search_job(
        query=params["query"],
        earliest_time=params["earliest_time"],
        latest_time=params["latest_time"],
    )

    base_get_events.wait_for_search_job_execution(
        event_search_job_uuid=event_search_job_uuid
    )

    requested_limit = params.get("limit", 100)
    limit = max(1, min(int(requested_limit), 100))

    response_events = base_get_events.http_session.get(
        f"{base_get_events.events_api_path}/search/jobs/{event_search_job_uuid}/events",
        params={"limit": limit, "offset": 0},
    )
    response_events.raise_for_status()
    response_content: dict = response_events.json()

    results: Optional[list] = response_content.get("items", [])
    return {"events": results}
