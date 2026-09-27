from dataclasses import dataclass

from ..integrations.http import probe_url
from ..integrations.mqtt import probe_mqtt
from ..integrations.network import ping, tcp_probe
from ..integrations.snmp import probe_snmp
from ..integrations.ssh import collect_linux


@dataclass
class ConnectionResult:
    ok: bool
    label: str
    details: str
    data: dict | None = None


def run_connection_test(device, method: str | None = None) -> ConnectionResult:
    method = method or device.connection or "auto"
    if method == "auto":
        method = _infer(device)

    if method == "ssh":
        result = collect_linux(device.address, device.username, device.port or 22)
        return ConnectionResult(
            result.ok,
            "SSH",
            result.error or f"Connected to {result.data.get('hostname', device.address)}",
            result.data,
        )
    if method in ("http", "https"):
        url = device.address
        if not url.startswith(("http://", "https://")):
            url = f"{method}://{url}"
        if device.port and "://" in url:
            scheme, rest = url.split("://", 1)
            if ":" not in rest.rsplit("/", 1)[0]:
                url = f"{scheme}://{rest.split('/', 1)[0]}:{device.port}" + ("/" + rest.split('/', 1)[1] if "/" in rest else "")
        result = probe_url(url)
        return ConnectionResult(
            result.get("reachable", False),
            "HTTP",
            f"HTTP {result.get('status', '—')} · {result.get('url', url)}\n{result.get('error', '')}".strip(),
            result,
        )
    if method == "mqtt":
        result = probe_mqtt(device.address, device.port or 1883)
        return ConnectionResult(
            result.get("reachable", False),
            "MQTT",
            f"MQTT port {device.port or 1883} · {result.get('latency_ms', '—')} ms\n{result.get('error', '')}".strip(),
            result,
        )
    if method == "snmp":
        community = device.metadata.get("snmp_community", "public")
        result = probe_snmp(device.address, community, device.port or 161)
        return ConnectionResult(
            result.get("reachable", False),
            "SNMP",
            result.get("sysdescr") or result.get("error", "SNMP check finished."),
            result,
        )
    if method == "ping":
        result = ping(device.address)
        return ConnectionResult(result["reachable"], "ICMP", f"Reachable: {result['reachable']}", result)
    if method in ("tcp", "serial", "ble", "smb", "rdp", "vnc"):
        port = device.port or {"tcp": 80, "smb": 445, "rdp": 3389, "vnc": 5900}.get(method, 0)
        if port:
            result = tcp_probe(device.address, port)
            return ConnectionResult(
                result.get("reachable", False),
                method.upper(),
                f"{device.address}:{port} · {result.get('latency_ms', '—')} ms\n{result.get('error', '')}".strip(),
                result,
            )
        return ConnectionResult(False, method.upper(), "This connection type needs a device-specific address or port.")
    return ConnectionResult(False, method.upper(), f"Unsupported connection type: {method}")


def _infer(device) -> str:
    if device.kind in ("server", "raspberry-pi") and device.username:
        return "ssh"
    if device.connection and device.connection != "auto":
        return device.connection
    if device.port == 22:
        return "ssh"
    return "ping"
