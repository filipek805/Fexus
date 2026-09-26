from pathlib import Path

from fexus.app.core.models import Device
from fexus.app.core.storage import Storage


def test_storage_round_trip(tmp_path: Path):
    db = Storage(tmp_path / "test.db")
    device = Device(id="1", name="pi", kind="raspberry-pi", address="192.168.1.10")
    db.save_device(device)

    loaded = db.list_devices()
    assert len(loaded) == 1
    assert loaded[0].name == "pi"
    assert loaded[0].address == "192.168.1.10"
    db.close()
