# Integrations

Fexus talks directly to local or remote equipment. No Fexus backend is required.

## SSH

Used for Linux servers, Raspberry Pis and other Unix systems. Fexus uses the local SSH key/agent and verifies hosts using the system known-hosts database.

## HTTP / HTTPS

Used for routers, NAS appliances, web dashboards and local HTTP APIs. Fexus performs a read-only GET health check.

## MQTT

The optional `paho-mqtt` dependency supports broker publishing. A basic TCP check works through the built-in connector even without the optional client.

```bash
python3 -m pip install --user --break-system-packages -e ".[mqtt]"
```

## SNMP

The Connect page performs a read-only SNMPv2c `sysDescr` query through the Net-SNMP `snmpget` command.

On Debian/Ubuntu:

```bash
sudo apt install -y snmp
```

## Docker

Optional Docker SDK support reads the local Docker socket.

```bash
python3 -m pip install --user --break-system-packages -e ".[docker]"
```

## libvirt

Fexus uses `virsh list --all` and related read-only commands.

## Serial / USB

Optional PySerial support enumerates locally attached serial devices.

```bash
python3 -m pip install --user --break-system-packages -e ".[serial]"
```

## Bluetooth LE

Optional Bleak support discovers nearby BLE advertisements.

```bash
python3 -m pip install --user --break-system-packages -e ".[ble]"
```

## mDNS

Optional Zeroconf support discovers common local services such as SSH, HTTP, HTTPS, SMB and MQTT.

```bash
python3 -m pip install --user --break-system-packages -e ".[mdns]"
```

## RDP / VNC

Fexus launches an installed external desktop client instead of implementing the remote desktop protocol itself.

## Wake-on-LAN

Fexus sends a standard magic packet to a stored MAC address.

## Network checks

Built-in network checks include:

- ICMP reachability
- TCP connection checks
- latency measurement

No cloud service is involved.
