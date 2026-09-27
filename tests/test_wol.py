import pytest

from fexus.app.integrations.wol import normalize_mac


def test_normalize_mac():
    assert normalize_mac("AA:BB:CC:DD:EE:FF") == "aabbccddeeff"


def test_invalid_mac():
    with pytest.raises(ValueError):
        normalize_mac("not-a-mac")
