import pytest
from connectors.core.connector import ConnectorError

import sekoia_io_xdr.health_check as health_module
import sekoia_io_xdr.runtime_connector as connector_module
import sekoia_io_xdr.utils as utils_module


def test_connector_execute_routes_operation(monkeypatch):
    called = {}

    def fake_operation(config, params):
        called["config"] = config
        called["params"] = params
        return {"ok": True}

    monkeypatch.setattr(connector_module, "add_comment_to_alert", fake_operation)

    connector = connector_module.Sekoiaio()
    result = connector.execute({"api_key": "k"}, "add_comment_to_alert", {"a": 1})

    assert result == {"ok": True}
    assert called["params"] == {"a": 1}


def test_connector_check_health_delegates(monkeypatch):
    monkeypatch.setattr(connector_module, "check", lambda config: "ok")
    connector = connector_module.Sekoiaio()
    assert connector.check_health({"api_key": "k"}) == "ok"


def test_health_check_success(monkeypatch):
    class FakeClient:
        def __init__(self, headers, verify=False, proxy=False):
            self.headers = headers

        def get_validate_resource(self):
            return "ok"

    monkeypatch.setattr(health_module, "Client", FakeClient)

    assert health_module.check({"api_key": "k", "verify_certificate": True}) == "ok"


def test_health_check_invalid_token(monkeypatch):
    class FakeClient:
        def __init__(self, headers, verify=False, proxy=False):
            pass

        def get_validate_resource(self):
            raise Exception("The token is invalid")

    monkeypatch.setattr(health_module, "Client", FakeClient)

    assert (
        health_module.check({"api_key": "k"})
        == "Authorization Error: make sure API Key is correctly set"
    )


def test_health_check_re_raises_other_errors(monkeypatch):
    class FakeClient:
        def __init__(self, headers, verify=False, proxy=False):
            pass

        def get_validate_resource(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(health_module, "Client", FakeClient)

    with pytest.raises(RuntimeError, match="boom"):
        health_module.check({"api_key": "k"})


def test_generic_api_action_headers_include_auth():
    action = utils_module.GenericAPIAction(
        {"api_key": "secret"},
        "GET",
        "https://example.local",
    )

    assert action._headers["Accept"] == "application/json"
    assert action._headers["Authorization"] == "Bearer secret"


def test_generic_api_action_success(monkeypatch):
    class Response:
        ok = True
        text = ""

        def json(self):
            return {"status": "ok"}

    monkeypatch.setattr(utils_module.requests, "request", lambda *a, **k: Response())
    monkeypatch.setattr(utils_module.dump, "dump_all", lambda _r: b"raw")

    action = utils_module.GenericAPIAction(
        {"api_key": "secret"},
        "GET",
        "https://example.local",
    )

    assert action.run() == {"status": "ok"}


def test_generic_api_action_error_raises_connector_error(monkeypatch):
    class Response:
        ok = False
        text = "bad"
        status_code = 400
        content = b"bad"

        def json(self):
            return {"error": "bad"}

    monkeypatch.setattr(utils_module.requests, "request", lambda *a, **k: Response())
    monkeypatch.setattr(utils_module.dump, "dump_all", lambda _r: b"raw")

    action = utils_module.GenericAPIAction(
        {"api_key": "secret"},
        "GET",
        "https://example.local",
    )

    with pytest.raises(ConnectorError):
        action.run()


def test_generic_api_action_logs_binary_error_when_json_parse_fails(monkeypatch):
    class Response:
        ok = False
        text = "bad"
        status_code = 500
        content = b"raw-body"

        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr(utils_module.requests, "request", lambda *a, **k: Response())
    monkeypatch.setattr(utils_module.dump, "dump_all", lambda _r: b"raw")

    action = utils_module.GenericAPIAction(
        {"api_key": "secret"},
        "GET",
        "https://example.local",
    )

    with pytest.raises(ConnectorError):
        action.run()


def test_generic_api_action_timeout_returns_none(monkeypatch):
    class RaiseRetrying:
        def __iter__(self):
            raise utils_module.RetryError(None)

    monkeypatch.setattr(utils_module, "Retrying", lambda **_kwargs: RaiseRetrying())

    action = utils_module.GenericAPIAction(
        {"api_key": "secret"},
        "GET",
        "https://example.local",
    )

    assert action.run() is None


def test_client_invalid_token_raises(monkeypatch):
    class Resp:
        def json(self):
            return {"message": "The token is invalid"}

    monkeypatch.setattr(utils_module.requests, "get", lambda *a, **k: Resp())
    client = utils_module.Client({"Authorization": "Bearer x"})

    with pytest.raises(Exception, match="the request failed"):
        client.get_validate_resource()


def test_client_valid_token_returns_ok(monkeypatch):
    class Resp:
        def json(self):
            return {"message": "ok"}

    monkeypatch.setattr(utils_module.requests, "get", lambda *a, **k: Resp())
    client = utils_module.Client({"Authorization": "Bearer x"})

    assert client.get_validate_resource() == "ok"


def test_base_get_events_configure_and_trigger(monkeypatch):
    base = utils_module.BaseGetEvents({"api_key": "k"})

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"uuid": "job-1"}

    calls = {}

    class FakeSession:
        def __init__(self):
            self.headers = None

        def mount(self, *_args, **_kwargs):
            return None

        def post(self, url, json=None):
            calls["url"] = url
            calls["json"] = json
            return Resp()

    monkeypatch.setattr(utils_module, "Session", FakeSession)

    session = base.configure_http_session()
    assert session.headers["Authorization"] == "Bearer k"

    job = base.trigger_event_search_job("q", "a", "b")
    assert job == "job-1"
    assert calls["json"]["term"] == "q"


def test_base_get_events_wait_until_done(monkeypatch):
    base = utils_module.BaseGetEvents({"api_key": "k"})

    class Resp:
        def __init__(self, status):
            self._status = status

        def raise_for_status(self):
            return None

        def json(self):
            return {"status": self._status}

    statuses = iter([Resp(1), Resp(2)])

    class FakeSession:
        def get(self, _url):
            return next(statuses)

    base.http_session = FakeSession()
    monkeypatch.setattr(utils_module.time, "sleep", lambda _s: None)

    times = iter([0, 1])
    monkeypatch.setattr(utils_module.time, "time", lambda: next(times))

    base.wait_for_search_job_execution("job-1")


def test_base_get_events_wait_timeout(monkeypatch):
    base = utils_module.BaseGetEvents({"api_key": "k"})

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": 1}

    class FakeSession:
        def get(self, _url):
            return Resp()

    base.http_session = FakeSession()
    monkeypatch.setattr(utils_module.time, "sleep", lambda _s: None)

    times = iter([0, 301])
    monkeypatch.setattr(utils_module.time, "time", lambda: next(times))

    with pytest.raises(TimeoutError, match="took more than"):
        base.wait_for_search_job_execution("job-1")
