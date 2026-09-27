import re
import shutil
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor


def _resolve(host: str) -> str:
    try:
        return socket.gethostbyaddr(host)[0]
    except OSError:
        return ""


def discover_neighbors() -> list[dict]:
    if shutil.which("ip"):
        try:
            output = subprocess.check_output(["ip", "neigh", "show"], text=True, timeout=3)
            result = []
            for line in output.splitlines():
                parts = line.split()
                if len(parts) < 5 or parts[0] == "failed":
                    continue
                ip = parts[0]
                mac = parts[4] if "lladdr" in parts else ""
                iface = parts[2] if len(parts) > 2 and parts[1] == "dev" else ""
                state = parts[-1]
                result.append({
                    "address": ip,
                    "mac": mac,
                    "name": _resolve(ip) or ip,
                    "detail": f"{iface} · {state}" if iface else state,
                    "source": "ARP/neighbor",
                    "kind": "network",
                })
            return _dedupe(result)
        except (OSError, subprocess.SubprocessError):
            pass

    if shutil.which("arp"):
        try:
            output = subprocess.check_output(["arp", "-a"], text=True, timeout=3)
            result = []
            for line in output.splitlines():
                match = re.search(r"\(([^)]+)\).*?([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})", line)
                if match:
                    result.append({
                        "address": match.group(1),
                        "mac": match.group(2),
                        "name": _resolve(match.group(1)) or match.group(1),
                        "detail": "ARP",
                        "source": "ARP",
                        "kind": "network",
                    })
            return _dedupe(result)
        except (OSError, subprocess.SubprocessError):
            pass
    return []


def discover_mdns(timeout: float = 3) -> list[dict]:
    try:
        from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
    except ImportError:
        return []

    service_types = [
        "_ssh._tcp.local.",
        "_http._tcp.local.",
        "_https._tcp.local.",
        "_smb._tcp.local.",
        "_mqtt._tcp.local.",
        "_ipp._tcp.local.",
    ]
    found = []

    class Listener(ServiceListener):
        def add_service(self, zc, service_type, name):
            info = zc.get_service_info(service_type, name, timeout=1000)
            if not info:
                return
            addresses = info.parsed_addresses()
            if not addresses:
                return
            protocol = service_type.split(".")[0].lstrip("_")
            found.append({
                "address": addresses[0],
                "port": info.port,
                "name": name.rstrip("."),
                "detail": f"{protocol}:{info.port}",
                "source": "mDNS",
                "kind": "network",
                "protocol": protocol,
            })

        def remove_service(self, *args):
            return None

        def update_service(self, *args):
            return None

    zc = Zeroconf()
    browsers = [ServiceBrowser(zc, service_type, Listener()) for service_type in service_types]
    import time
    time.sleep(timeout)
    for _ in browsers:
        pass
    zc.close()
    return _dedupe(found)


def discover_local() -> list[dict]:
    neighbors = discover_neighbors()
    with ThreadPoolExecutor(max_workers=1) as pool:
        mdns_future = pool.submit(discover_mdns)
        try:
            mdns = mdns_future.result(timeout=4)
        except Exception:
            mdns = []
    return _dedupe(neighbors + mdns)


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for item in items:
        key = (item.get("address", ""), item.get("port", ""), item.get("protocol", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
