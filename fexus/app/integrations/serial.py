def list_serial_devices():
    try:
        import serial.tools.list_ports
        return [
            {
                "device": p.device,
                "description": p.description or "",
                "manufacturer": p.manufacturer or "",
                "vid": p.vid,
                "pid": p.pid,
            }
            for p in serial.tools.list_ports.comports()
        ]
    except Exception:
        return []
