import socket
import subprocess
import time


def tcp_probe(host: str, port: int, timeout=1.5) -> dict:
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return {"reachable": True, "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
    except OSError as exc:
        return {"reachable": False, "latency_ms": None, "error": str(exc)}


def ping(host: str, timeout=1.5) -> dict:
    command = ["ping", "-c", "1", "-W", str(max(1, int(timeout * 1000))), host]
    if subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        return {"reachable": True}
    return {"reachable": False}
