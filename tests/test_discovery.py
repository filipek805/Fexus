from fexus.app.integrations.discovery import _dedupe


def test_discovery_dedupe():
    items = [
        {"address": "192.168.1.2", "port": 22, "protocol": "ssh"},
        {"address": "192.168.1.2", "port": 22, "protocol": "ssh"},
    ]
    assert len(_dedupe(items)) == 1
