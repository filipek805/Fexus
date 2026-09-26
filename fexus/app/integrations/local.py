import os
import platform
import socket
import time

import psutil


def collect_local() -> dict:
    root = psutil.disk_usage("/")
    vm = psutil.virtual_memory()
    net = psutil.net_io_counters()
    temps = {}
    try:
        for name, items in psutil.sensors_temperatures().items():
            temps[name] = [{"label": x.label, "current": x.current} for x in items]
    except Exception:
        pass
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_percent": psutil.cpu_percent(interval=0.15),
        "memory_percent": vm.percent,
        "memory_total": vm.total,
        "disk_percent": root.percent,
        "disk_total": root.total,
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "network_rx": net.bytes_recv,
        "network_tx": net.bytes_sent,
        "temperatures": temps,
        "user": os.getenv("USER") or os.getenv("USERNAME") or "",
    }
