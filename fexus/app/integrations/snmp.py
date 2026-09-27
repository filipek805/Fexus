import shutil
import subprocess


def probe_snmp(host: str, community: str = "public", port: int = 161, timeout: int = 2) -> dict:
    command = shutil.which("snmpget")
    if not command:
        return {"reachable": False, "error": "snmpget is not installed (Net-SNMP)."}
    target = f"udp:{host}:{port}"
    args = [command, "-v2c", "-c", community, "-t", str(timeout), "-r", "0", target, "1.3.6.1.2.1.1.1.0"]
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout + 2)
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}
    if completed.returncode == 0:
        return {"reachable": True, "sysdescr": completed.stdout.strip()}
    return {"reachable": False, "error": (completed.stderr or completed.stdout).strip()}
