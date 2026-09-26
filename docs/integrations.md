# Integrations

## SSH

Used for Linux servers and Raspberry Pis.

Fexus looks for normal SSH keys and the user's SSH agent.

No Fexus daemon is required.

## Docker

Optional dependency:

```bash
pip install -e ".[docker]"
```

Reads the local Docker socket.

The first release is intentionally read-only.

## libvirt

Uses `virsh`.

```bash
virsh list --all
```

No Fexus daemon is required.

## Serial

Optional:

```bash
pip install -e ".[serial]"
```

Serial enumeration uses pyserial.

## SNMP

Optional:

```bash
pip install -e ".[snmp]"
```

SNMP profiles should be added as focused integrations.

## Network checks

The base application can perform:

- ping reachability
- TCP connection checks
- latency measurement

No cloud service is involved.
