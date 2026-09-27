import shutil
import subprocess


def launch_remote(kind: str, address: str, port: int | None = None, username: str = "") -> dict:
    kind = kind.lower()
    if kind == "rdp":
        command = _find_first("xfreerdp3", "xfreerdp", "remmina")
        if not command:
            return {"ok": False, "error": "Install an RDP client such as FreeRDP or Remmina."}
        if "freerdp" in command:
            target = f"{address}:{port or 3389}"
            args = [command, f"/v:{target}"]
            if username:
                args.append(f"/u:{username}")
        else:
            target = f"rdp://{address}:{port or 3389}"
            args = [command, target]
    elif kind == "vnc":
        command = _find_first("remmina", "vncviewer", "vinagre", "krdc")
        if not command:
            return {"ok": False, "error": "Install a VNC client such as Remmina or TigerVNC."}
        target = f"vnc://{address}:{port or 5900}"
        args = [command, target]
    else:
        return {"ok": False, "error": f"Unsupported remote client: {kind}"}

    try:
        subprocess.Popen(args, start_new_session=True)
        return {"ok": True, "command": " ".join(args)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def _find_first(*commands: str) -> str | None:
    for command in commands:
        path = shutil.which(command)
        if path:
            return path
    return None
