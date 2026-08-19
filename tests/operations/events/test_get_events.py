from unittest.mock import MagicMock, patch

from django.conf import settings


def test_get_events(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.events.get_events import get_events

    with patch("sekoia_io_xdr.operations.events.get_events.BaseGetEvents") as base_cls:
        base = base_cls.return_value
        base.events_api_path = "https://app.sekoia.io/api/v1/sic/events"
        base.trigger_event_search_job.return_value = "job-123"

        response = MagicMock()
        response.json.return_value = {
            "total": 1,
            "items": [{"uuid": "evt-1", "message": "sample"}],
        }
        base.http_session.get.return_value = response

        result = get_events(
            config=connector_config,
            params={
                "query": "id:AL123",
                "earliest_time": "2024-01-01T00:00:00.000Z",
                "latest_time": "2024-01-01T01:00:00.000Z",
                "limit": 50,
            },
        )

        base.configure_http_session.assert_called_once()
        base.trigger_event_search_job.assert_called_once_with(
            query="id:AL123",
            earliest_time="2024-01-01T00:00:00.000Z",
            latest_time="2024-01-01T01:00:00.000Z",
        )
        base.wait_for_search_job_execution.assert_called_once_with(
            event_search_job_uuid="job-123"
        )
        base.http_session.get.assert_called_once_with(
            "https://app.sekoia.io/api/v1/sic/events/search/jobs/job-123/events",
            params={"limit": 50, "offset": 0},
        )
        assert result == {"events": [{"uuid": "evt-1", "message": "sample"}]}


def test_get_events_default_limit(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.events.get_events import get_events

    with patch("sekoia_io_xdr.operations.events.get_events.BaseGetEvents") as base_cls:
        base = base_cls.return_value
        base.events_api_path = "https://app.sekoia.io/api/v1/sic/events"
        base.trigger_event_search_job.return_value = "job-123"

        response = MagicMock()
        response.json.return_value = {"total": 0, "items": []}
        base.http_session.get.return_value = response

        get_events(
            config=connector_config,
            params={
                "query": "id:AL123",
                "earliest_time": "2024-01-01T00:00:00.000Z",
                "latest_time": "2024-01-01T01:00:00.000Z",
            },
        )

        base.http_session.get.assert_called_once_with(
            "https://app.sekoia.io/api/v1/sic/events/search/jobs/job-123/events",
            params={"limit": 100, "offset": 0},
        )


def test_get_events_limit_is_clamped_between_1_and_100(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.events.get_events import get_events

    with patch("sekoia_io_xdr.operations.events.get_events.BaseGetEvents") as base_cls:
        base = base_cls.return_value
        base.events_api_path = "https://app.sekoia.io/api/v1/sic/events"
        base.trigger_event_search_job.return_value = "job-123"

        response = MagicMock()
        response.json.return_value = {"items": []}
        base.http_session.get.return_value = response

        get_events(
            config=connector_config,
            params={
                "query": "id:AL123",
                "earliest_time": "2024-01-01T00:00:00.000Z",
                "latest_time": "2024-01-01T01:00:00.000Z",
                "limit": 0,
            },
        )

        assert base.http_session.get.call_args.kwargs["params"]["limit"] == 1


def test_get_events_operation_helpers():
    settings.configure()
    from sekoia_io_xdr.operations.events.get_events import (
        GetEventsOperation,
        GetEventsParams,
    )

    op = GetEventsOperation()
    parsed = GetEventsParams(
        query="q",
        earliest_time="2024-01-01T00:00:00.000Z",
        latest_time="2024-01-01T01:00:00.000Z",
    )

    assert op.build_endpoint(parsed) == ""
    assert op.build_payload(parsed) is None
