# Fexus

> A free, local-first desktop control center for homelabs, servers, Raspberry Pis, ESP devices, Docker, virtual machines, NAS systems, and network equipment.

Fexus is a **desktop application**, not a website. It has no required Fexus cloud, no subscription, and no paid API. Device communication happens locally or directly over the protocols the devices already support.

## 0.3.0 highlights

- Dashboard, device inventory, connection workspace and event history
- SSH for Linux servers and Raspberry Pis
- HTTP / HTTPS health checks
- MQTT broker checks and optional message publishing
- SNMP read-only checks through Net-SNMP
- ICMP and TCP reachability checks
- RDP / VNC launch through installed desktop clients
- Wake-on-LAN
- LAN neighbor discovery from the local ARP/neighbor table
- Optional mDNS discovery
- USB / serial discovery for embedded hardware
- Optional Bluetooth LE discovery
- Docker and libvirt inventory
- Local SQLite storage with automatic 0.2.x → 0.3.0 migration

## Completely free

Fexus is intended to remain free and open source. There is no paid tier, cloud lock-in, required account, analytics requirement, paid API, or license server.

Optional donations can help support development, hardware and testing.

## Quick start

### Linux

Install Python 3.11+. On Debian/Ubuntu, Qt applications may also need the XCB cursor runtime package:

```bash
sudo apt update
sudo apt install -y python3-venv libxcb-cursor0

git clone https://github.com/filipek805/fexus.git
cd fexus

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
fexus
```

Optional integrations:

```bash
pip install -e ".[docker,serial,mqtt,ble,mdns]"
```

For SNMP checks, install Net-SNMP on the host. On Debian/Ubuntu:

```bash
sudo apt install -y snmp
```

### Windows

```powershell
git clone https://github.com/filipek805/fexus.git
cd fexus

py -m venv .venv
.venv\Scripts\activate

pip install -e .
fexus
```

Optional BLE, MQTT, and mDNS support can be installed with the same extras command.

### macOS

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
fexus
```

## First launch

Use **Discover** to find devices Fexus can already see, or use **Devices → Add device** for a known address. The **Connect** page lets you test a stored device or enter a manual address.

### Connection methods

| Method | Main use |
|---|---|
| SSH | Linux servers, Raspberry Pis, NAS appliances |
| HTTP / HTTPS | Routers, dashboards, local APIs |
| MQTT | ESP32/ESP8266 and IoT brokers |
| SNMP | Switches, routers, NAS and appliances |
| ICMP | Basic reachability |
| TCP | Check a service port |
| Serial / USB | ESP boards, Pico, embedded hardware |
| BLE | Nearby Bluetooth Low Energy hardware |
| RDP | Windows desktops/servers |
| VNC | Remote graphical systems |
| SMB | NAS/file-server port checks |

## Setting up the other device

See **[Device setup and connection tutorials](docs/device-setup.md)** for step-by-step instructions for SSH servers and Raspberry Pis, Windows, ESP32/ESP8266 MQTT, USB serial, BLE, routers, switches, NAS, SNMP, RDP, VNC, SMB, Wake-on-LAN, Docker, libvirt and network checks.

## Discovery

### LAN neighbors

On Linux Fexus reads the local neighbor table instead of brute-force scanning the entire subnet. This keeps discovery quick and low-impact.

### mDNS

Optional mDNS discovery looks for common local services such as SSH, HTTP, HTTPS, SMB, MQTT and printing. Install:

```bash
pip install -e ".[mdns]"
```

### USB / Serial

Install:

```bash
pip install -e ".[serial]"
```

Then connect an ESP32, ESP8266, Pico or other serial device over USB.

### Bluetooth LE

Install:

```bash
pip install -e ".[ble]"
```

Fexus will list nearby BLE advertisements when the host Bluetooth stack permits access.

## SSH

Fexus uses your existing SSH keys and agent. It does not install a Fexus agent on the target machine. Host keys are verified against the system SSH known-hosts database.

Create a key if needed:

```bash
ssh-keygen -t ed25519
```

Copy it:

```bash
ssh-copy-id user@192.168.1.20
```

Confirm normal SSH works before adding the device to Fexus.

## MQTT

Install the optional client:

```bash
pip install -e ".[mqtt]"
```

On **Connect**, choose MQTT, enter the broker address/port, and optionally provide credentials. The same page can publish a message to a topic.

## SNMP

Fexus performs a read-only system-description check using Net-SNMP:

```bash
sudo apt install -y snmp
```

Use the community field on the Connect page when the device does not use the common `public` read community.

## RDP / VNC

Fexus does not embed a remote-desktop server. It launches a client already installed on your machine, such as FreeRDP or Remmina.

## Wake-on-LAN

Store a device MAC address and use **Connect → Wake on LAN**. The target hardware and network must have Wake-on-LAN enabled.

## Docker

Install the optional Docker SDK:

```bash
pip install -e ".[docker]"
```

Fexus reads the local Docker socket. The inventory view is read-only.

## Virtual machines

On a Linux host with libvirt:

```bash
virsh list --all
```

Fexus reads VM names and states through `virsh`.

## NAS and network equipment

Add appliances directly by IP/hostname and choose HTTP, HTTPS, SNMP, TCP or ICMP depending on what the device exposes.

## Data and privacy

Fexus stores local inventory and history in:

```text
Linux:   ~/.local/share/fexus/fexus.db
macOS:   ~/Library/Application Support/Fexus/fexus.db
Windows: %LOCALAPPDATA%\Fexus\fexus.db
```

There is no required cloud account.
