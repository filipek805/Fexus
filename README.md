# Fexus
follow me on tiktok bitcoinmuncher and anyone who wants to donate to help fund the project shall text me on tiktok
> A free, local-first desktop control center for homelabs, servers, Raspberry Pis, ESP devices, Docker, virtual machines, NAS systems, and network equipment.

Fexus is a **desktop application**, not a website.

There is no Fexus cloud, no Fexus account, no subscription, and no paid API required.

Your inventory and local history live on your own computer.

## What Fexus does

Fexus gives you one desktop application for your lab:

- Linux servers and desktops
- Raspberry Pis
- Docker hosts and containers
- libvirt virtual machines
- NAS systems
- routers, switches, access points, and other network equipment
- ESP32 / ESP8266 boards
- local hardware and USB devices
- SSH-connected machines

The design goal is simple:

**Install Fexus → open the app → add your machines → see your whole lab.**

## Why there is no API

The previous prototype used a web API because it was structured like a browser dashboard.

Fexus no longer requires that architecture.

The desktop app talks to devices using the protocols they already support:

- local OS APIs
- SSH
- Docker
- libvirt
- ICMP/TCP checks
- SNMP when enabled
- serial/USB for embedded boards

These are communication protocols, not a Fexus cloud service.

You do not need to buy an API key.

## Completely free

Fexus is intended to remain free and open source.

There is:

- no paid tier
- no cloud lock-in
- no required account
- no analytics requirement
- no paid API
- no license server

You can run the software entirely on your own hardware.

The project can still accept optional donations to help pay for development, hardware and testing.

## Current desktop application

The first desktop release provides:

- dashboard
- device inventory
- device groups and tags
- local machine monitoring
- SSH host configuration
- server/Raspberry Pi discovery over SSH
- Docker container inventory
- libvirt VM inventory
- network reachability checks
- TCP service checks
- serial device discovery
- event log
- local SQLite storage
- light/dark interface foundation
- no browser window
- no background cloud service

## Quick start

### Linux

Install Python 3.11+.

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus

python3 -m venv .venv
source .venv/bin/activate

pip install -e .

fexus
```

Or:

```bash
python -m fexus.app
```

### Windows

Install Python 3.11+ from python.org, then:

```powershell
git clone https://github.com/filipek805/fexus.git
cd fexus

py -m venv .venv
.venv\Scripts\activate

pip install -e .

fexus
```

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

When Fexus opens:

1. The **Overview** screen shows your local machine.
2. Open **Devices**.
3. Select **Add device**.
4. Choose the device type.
5. Enter the address or hostname.
6. For servers and Raspberry Pis, add an SSH username.
7. Save it.
8. Fexus tests the connection and starts collecting information.

You can group devices with tags such as:

```text
core
servers
raspberry-pi
docker
nas
network
iot
```

## Connecting a Linux server or Raspberry Pi

Fexus uses SSH instead of requiring a Fexus server or agent.

Example:

```text
Type:       Server
Name:       Main server
Address:    192.168.1.20
SSH port:   22
Username:   filip
```

Fexus can then query read-only system information through SSH.

The initial implementation uses normal Linux commands rather than installing a privileged daemon.

### SSH keys

SSH keys are recommended.

Create one if you do not already have one:

```bash
ssh-keygen -t ed25519
```

Copy it to the machine:

```bash
ssh-copy-id user@192.168.1.20
```

Fexus can then connect without asking for your password every time.

## Docker

For a local Docker host, Fexus can inspect Docker through the local Docker socket.

For a remote Docker host, the preferred approach is SSH.

Fexus's initial Docker integration is read-only:

- container name
- image
- status
- ports
- labels
- restart policy where available

The application does not need Docker running if you are only monitoring ordinary servers.

## Virtual machines

Fexus can discover libvirt guests from machines where `virsh` is available.

It can show:

- VM name
- running/shut off state
- host
- basic metadata

The first release intentionally avoids destructive VM operations.

## NAS systems

Add your NAS as a network device.

Fexus can check:

- host reachability
- common service ports
- hostname
- response time

Optional SNMP support can provide richer information from supported appliances.

## Network equipment

You can add routers, switches, access points and firewalls.

Fexus can monitor:

- reachability
- latency
- TCP ports
- optional SNMP metrics

## ESP32 / ESP8266

Fexus can discover USB/serial devices and show them in the inventory.

For richer telemetry, an ESP integration can communicate with a broker or direct serial connection that you control.

Nothing is sent to Fexus servers because there are no Fexus servers.

## Data storage

Fexus stores local application data in the user's application data directory.

SQLite is used for the local database.

No remote database is required.

## Repository structure

```text
fexus/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   ├── dependabot.yml
│   └── FUNDING.yml
├── docs/
│   ├── setup.md
│   ├── architecture.md
│   ├── integrations.md
│   ├── building.md
│   └── troubleshooting.md
├── fexus/
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── integrations/
│       └── ui/
├── tests/
├── .env.example
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── SECURITY.md
├── SUPPORT.md
├── CHANGELOG.md
├── CITATION.cff
├── Makefile
└── pyproject.toml
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

Run directly from the repository:

```bash
python -m fexus.app
```

## Build an executable

See [`docs/building.md`](docs/building.md).

The project can be packaged into a standalone executable using PyInstaller.

## Security

Fexus does not run a cloud backend.

That removes a whole category of account and hosted-service risk, but the app can still connect to privileged machines over SSH.

Use least-privilege accounts and SSH keys where possible.

Read [`SECURITY.md`](SECURITY.md) before connecting production infrastructure.

## Roadmap

- [ ] native desktop packaging for Linux
- [ ] Windows installer
- [ ] macOS app bundle
- [ ] richer SSH metrics
- [ ] Docker actions with explicit confirmation
- [ ] Proxmox integration
- [ ] TrueNAS and Synology profiles
- [ ] SNMP device profiles
- [ ] ESP serial telemetry
- [ ] ESP Wi-Fi telemetry
- [ ] service checks
- [ ] historical charts
- [ ] alert rules
- [ ] notifications
- [ ] Wake-on-LAN
- [ ] backup checks
- [ ] plugin SDK
- [ ] import/export
- [ ] multi-site inventory
- [ ] optional remote agent for networks where SSH is unavailable

## Support development

Fexus is free to use.

Optional donations help cover hardware, test devices, hosting for project infrastructure, and development time.

Replace the placeholder in `.github/FUNDING.yml` with your Buy Me a Coffee username before publishing.

## License

Fexus is released under the MIT License.
