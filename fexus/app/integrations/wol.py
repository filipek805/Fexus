import re
import socket
import struct

_MAC_RE = re.compile(r"^[0-9A-Fa-f]{12}$")


def normalize_mac(mac: str) -> str:
    compact = re.sub(r"[^0-9A-Fa-f]", "", mac)
    if not _MAC_RE.match(compact):
        raise ValueError("Invalid MAC address")
    return compact.lower()


def wake_on_lan(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> dict:
    try:
        compact = normalize_mac(mac)
        packet = b"\xff" * 6 + bytes.fromhex(compact) * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, (broadcast, port))
        return {"ok": True, "mac": compact, "broadcast": broadcast, "port": port}
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
