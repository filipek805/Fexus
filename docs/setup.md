# Fexus setup

Fexus is a native desktop application. You do **not** deploy a web server.

## Linux / Debian / Ubuntu / Linux Mint

Fexus does not require a virtual environment. Install the runtime packages first:

```bash
sudo apt update
sudo apt install -y python3 python3-pip libxcb-cursor0
```

Then:

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus
make install
```

Start it from the application menu or run:

```bash
make run
```

Direct module launch also works:

```bash
python3 -m fexus
```

`make install` installs a user-level desktop launcher. If `~/Desktop` exists, it also creates `~/Desktop/Fexus.desktop`.

For a standalone executable that does not need Python at runtime:

```bash
make install-app
```

Optional integrations:

```bash
python3 -m pip install --user --break-system-packages -e ".[docker,serial,mqtt,ble,mdns]"
```

SNMP needs Net-SNMP on the host:

```bash
sudo apt install -y snmp
```

## Device-by-device setup

For the target-side steps—enabling SSH, configuring an MQTT broker, preparing an ESP/Pico serial connection, enabling SNMP, setting up RDP/VNC/SMB, Wake-on-LAN and more, see [device-setup.md](device-setup.md).

## Add a server

Open **Devices → Add device** and use:

```text
Name: Main Server
Type: server
Connection: ssh
Address: 192.168.1.20
Port: 22
SSH username: filip
Tags: server, docker
```

Fexus uses the system SSH known-hosts file. First connect normally with `ssh` so the host key is known and trusted.

## Discover devices

Open **Discover** and use:

- **LAN neighbors** for the local ARP/neighbor table
- **mDNS** for local network services
- **USB / Serial** for embedded devices
- **Bluetooth LE** for nearby BLE hardware

Select a discovered entry and click **Add selected**.

## Connect

The **Connect** workspace supports:

- SSH
- HTTP / HTTPS
- MQTT
- SNMP
- ICMP
- TCP
- SMB port checks
- RDP / VNC client launching
- Wake-on-LAN

MQTT publishing needs the `mqtt` extra. RDP/VNC needs a compatible desktop client already installed on the host.

## Storage

Fexus uses SQLite locally:

```text
Linux:   ~/.local/share/fexus/fexus.db
macOS:   ~/Library/Application Support/Fexus/fexus.db
Windows: %LOCALAPPDATA%\Fexus\fexus.db
```

Upgrading from 0.2.x adds the new connection column automatically.
