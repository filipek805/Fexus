# Architecture

Fexus is a desktop application with local persistence.

```text
┌──────────────────────────────────────────────────────────┐
│                         FEXUS                            │
│                    PySide6 desktop UI                    │
├──────────────────────────────────────────────────────────┤
│                     Application core                     │
│       inventory · events · connection dispatcher        │
├──────────────────────────────────────────────────────────┤
│                       Discovery                          │
│          LAN/ARP · mDNS · USB/serial · BLE              │
├──────────────────────────────────────────────────────────┤
│                      Integrations                        │
│ SSH · HTTP · MQTT · SNMP · TCP · ICMP · Docker · VMs   │
│ Serial · BLE · SMB · RDP · VNC · Wake-on-LAN            │
├──────────────────────────────────────────────────────────┤
│                         SQLite                           │
└──────────────────────────────────────────────────────────┘
```

The application does not require a Fexus backend. Each integration is isolated so the UI can use a common `ConnectionResult` without knowing protocol-specific details.

### Safety model

The 0.3.0 update keeps inventory operations read-only by default. Explicit actions are limited to user-triggered operations such as MQTT publish, Wake-on-LAN and opening an external remote client. SSH host verification uses the system known-hosts database.
