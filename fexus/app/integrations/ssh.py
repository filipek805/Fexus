from dataclasses import dataclass


@dataclass
class SSHResult:
    ok: bool
    data: dict
    error: str = ""


def collect_linux(host: str, username: str, port: int = 22, timeout: float = 4) -> SSHResult:
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=username,
            timeout=timeout,
            look_for_keys=True,
            allow_agent=True,
        )

        command = r"""
        printf 'HOST=%s\n' "$(hostname)"
        printf 'KERNEL=%s\n' "$(uname -sr)"
        printf 'UPTIME=%s\n' "$(awk '{print int($1)}' /proc/uptime 2>/dev/null || true)"
        printf 'LOAD=%s\n' "$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || true)"
        printf 'MEM=%s\n' "$(free -m 2>/dev/null | awk '/Mem:/ {printf \"%.1f\", ($3/$2)*100}' || true)"
        printf 'DISK=%s\n' "$(df -P / 2>/dev/null | awk 'NR==2 {gsub(/%/,\"\",$5); print $5}' || true)"
        """
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        raw = stdout.read().decode(errors="replace")
        error = stderr.read().decode(errors="replace").strip()
        client.close()

        data = {}
        for line in raw.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.lower()] = value.strip()

        if error:
            data["stderr"] = error

        return SSHResult(True, data)
    except Exception as exc:
        return SSHResult(False, {}, str(exc))
