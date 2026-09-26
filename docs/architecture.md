# Architecture

Fexus is a desktop application with local persistence.

```text
┌──────────────────────────────────────────────┐
│                    FEXUS                     │
│              PySide6 desktop UI             │
├──────────────────────────────────────────────┤
│              Local application core          │
│    inventory · events · configuration        │
├──────────────────────────────────────────────┤
│                 Integrations                 │
│                                              │
│ OS      SSH      Docker      libvirt         │
│ Network SNMP     Serial     Future plugins   │
├──────────────────────────────────────────────┤
│                 SQLite                       │
└──────────────────────────────────────────────┘
```

The application does not require a Fexus backend.

## Communication

Fexus talks directly to the systems being monitored.

Examples:

- SSH for Linux servers and Raspberry Pis
- Docker SDK for local Docker
- `virsh` for local libvirt
- ICMP/TCP for network checks
- serial/USB for embedded devices
- SNMP for supported network appliances

## Why this model

A local desktop application is easier to self-host and easier to trust.

The initial release intentionally favors read-only operations.

Write operations can be added later with explicit confirmation and audit logging.
