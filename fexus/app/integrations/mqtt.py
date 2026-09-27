import socket


def probe_mqtt(host: str, port: int = 1883, timeout: float = 3) -> dict:
    try:
        started = __import__("time").perf_counter()
        with socket.create_connection((host, port), timeout=timeout):
            latency = round((__import__("time").perf_counter() - started) * 1000, 2)
        return {"reachable": True, "latency_ms": latency, "port": port}
    except OSError as exc:
        return {"reachable": False, "port": port, "error": str(exc)}


def publish(topic: str, payload: str, host: str, port: int = 1883, username: str = "", password: str = "") -> dict:
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        return {"ok": False, "error": "Install MQTT support with: pip install -e '.[mqtt]'"}

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if username:
        client.username_pw_set(username, password or None)
    try:
        client.connect(host, port, 5)
        client.loop_start()
        info = client.publish(topic, payload, qos=0)
        info.wait_for_publish(timeout=5)
        client.loop_stop()
        client.disconnect()
        return {"ok": info.is_published()}
    except Exception as exc:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
        return {"ok": False, "error": str(exc)}
