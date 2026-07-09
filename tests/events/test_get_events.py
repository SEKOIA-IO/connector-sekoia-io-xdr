from unittest.mock import MagicMock, patch

from django.conf import settings


def test_get_events(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.events.get_events import get_events

    with patch("connector_sekoia_io_xdr.events.get_events.BaseGetEvents") as base_cls:
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
        assert result == {"events": [{"uuid": "evt-1", "message": "sample"}]}
