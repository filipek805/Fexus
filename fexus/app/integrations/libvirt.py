import shutil
import subprocess


def list_local_vms():
    if not shutil.which("virsh"):
        return []
    try:
        output = subprocess.check_output(
            ["virsh", "list", "--all", "--name"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=4,
        )
        result = []
        for name in output.splitlines():
            name = name.strip()
            if not name:
                continue
            state = subprocess.check_output(
                ["virsh", "domstate", name],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=3,
            ).strip()
            result.append({"name": name, "status": state})
        return result
    except Exception:
        return []
