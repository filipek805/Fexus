from types import SimpleNamespace

from fexus.app.core.connectors import run_connection_test
from fexus.app.integrations.http import probe_url


def test_auto_connection_without_username_uses_ping(monkeypatch):
    monkeypatch.setattr("fexus.app.core.connectors.ping", lambda host: {"reachable": True})
    result = run_connection_test(SimpleNamespace(connection="auto", kind="network", address="127.0.0.1", port=None, username="", metadata={}))
    assert result.ok
    assert result.label == "ICMP"


def test_http_invalid_url_is_reported():
    result = probe_url("not a valid url")
    assert result["reachable"] is False
