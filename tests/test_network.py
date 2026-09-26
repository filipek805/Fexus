from fexus.app.integrations.network import tcp_probe


def test_tcp_probe_bad_port():
    result = tcp_probe("127.0.0.1", 1, timeout=0.05)
    assert "reachable" in result
