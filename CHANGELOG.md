# Changelog

## 0.3.0

- Added a reusable connection layer for SSH, HTTP/HTTPS, MQTT, SNMP, ICMP, TCP, SMB, RDP and VNC checks
- Added a dedicated Connect workspace
- Added LAN neighbor discovery from the local ARP/neighbor table
- Added optional mDNS service discovery
- Added optional Bluetooth LE discovery
- Added richer USB/serial discovery
- Added Wake-on-LAN
- Added optional MQTT publish support
- Added optional external RDP/VNC client launching
- Added persistent connection type and safe SQLite migration for existing 0.2.x databases
- Expanded device types for NAS, IoT, Bluetooth, desktops and VMs
- Improved device search and connection status tracking
- Documented Debian/Ubuntu Qt runtime requirements
- Added a device-side setup tutorial for configuring target devices before connecting them to Fexus

## 0.2.0

- Reworked Fexus into a native desktop application
- Removed the required web dashboard/backend architecture
- Added embedded SQLite storage
- Added local machine monitoring
- Added SSH server/Raspberry Pi discovery
- Added Docker discovery
- Added libvirt VM discovery
- Added network reachability/TCP checks
- Added serial device discovery
- Added desktop-first setup documentation
