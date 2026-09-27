import asyncio


def list_ble_devices(timeout: float = 4) -> list[dict]:
    try:
        from bleak import BleakScanner
    except ImportError:
        return []

    async def scan():
        found = await BleakScanner.discover(timeout=timeout, return_adv=True)
        result = []
        for address, (device, advertisement) in found.items():
            result.append({
                "address": address,
                "name": device.name or advertisement.local_name or "BLE device",
                "rssi": getattr(advertisement, "rssi", None),
                "source": "BLE",
                "kind": "bluetooth",
            })
        return result

    try:
        return asyncio.run(scan())
    except RuntimeError:
        return []
    except Exception:
        return []
