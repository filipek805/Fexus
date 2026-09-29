# Fexus

> A free, local-first desktop control center for homelabs, servers, Raspberry Pis, ESP devices, Docker, virtual machines, NAS systems, and network equipment.

Fexus is a desktop application, not a website.

It is designed to give you one place to discover, monitor, connect to, and manage the hardware and services around you without requiring a Fexus cloud account or paid API.

Fexus is free and open source.

## 0.3.0

Current capabilities include:

* Dashboard, device inventory, connection workspace and event history
* SSH connections for Linux servers and Raspberry Pis
* HTTP / HTTPS health checks
* MQTT broker checks and message publishing
* SNMP read-only checks
* ICMP and TCP reachability checks
* RDP / VNC launching through installed desktop clients
* Wake-on-LAN
* LAN neighbor discovery
* Optional mDNS discovery
* USB / serial discovery for embedded hardware
* Optional Bluetooth Low Energy discovery
* Docker inventory
* libvirt virtual machine inventory
* Local SQLite storage
* Automatic database migration from 0.2.x to 0.3.0

## Completely free

Fexus is intended to remain free and open source.

There is:

* No Fexus cloud requirement
* No subscription
* No paid API
* No required account
* No license server
* No analytics requirement
* No cloud lock-in

Optional donations can help support development, hardware, and testing.

## Requirements

* Python 3.11 or newer
* Linux, Windows, or macOS
* Git
* Internet access for the initial Python package installation

### Linux

On Debian/Ubuntu-based systems, install the basic requirements:

```bash
sudo apt update
sudo apt install -y python3 python3-pip git libxcb-cursor0
```

Fexus **does not require a virtual environment**.

## Quick start

### Linux

Clone the repository:

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus
```

Install Fexus for your user account:

```bash
make install
```

Start Fexus:

```bash
make run
```

You can also run the installed command directly:

```bash
fexus
```

If `fexus` is not found after installation, make sure your local Python binary directory is in `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

To make that permanent on most Linux systems:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Windows

Clone the repository:

```powershell
git clone https://github.com/filipek805/fexus.git
cd fexus
```

Install it for your user account:

```powershell
py -m pip install --user -e .
```

Run:

```powershell
fexus
```

No `.venv` is required.

### macOS

Clone the repository:

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus
```

Install it for your user account:

```bash
python3 -m pip install --user -e .
```

Run:

```bash
fexus
```

No `.venv` is required.

## Optional integrations

Fexus keeps several integrations optional so a basic installation stays lightweight.

### Docker

```bash
python3 -m pip install --user --break-system-packages -e ".[docker]"
```

Fexus reads the local Docker socket and displays Docker inventory.

### Serial / USB

Useful for ESP32, ESP8266, Raspberry Pi Pico and other serial devices:

```bash
python3 -m pip install --user --break-system-packages -e ".[serial]"
```

### MQTT

```bash
python3 -m pip install --user --break-system-packages -e ".[mqtt]"
```

This enables MQTT broker checks and message publishing.

### Bluetooth Low Energy

```bash
python3 -m pip install --user --break-system-packages -e ".[ble]"
```

Fexus can discover nearby BLE advertisements when the operating system permits access.

### mDNS

```bash
python3 -m pip install --user --break-system-packages -e ".[mdns]"
```

This enables local service discovery through mDNS.

### SNMP

Install the Python integration:

```bash
python3 -m pip install --user --break-system-packages -e ".[snmp]"
```

On Debian/Ubuntu, also install Net-SNMP:

```bash
sudo apt install -y snmp
```

## Install everything

For a development machine where you want all optional integrations:

```bash
python3 -m pip install --user --break-system-packages \
  -e ".[docker,serial,mqtt,ble,mdns,snmp,dev]"
```

## Makefile

Fexus includes a Makefile for common development tasks.

Install:

```bash
make install
```

Install development dependencies:

```bash
make dev
```

Run tests:

```bash
make test
```

Run the linter:

```bash
make lint
```

Start Fexus:

```bash
make run
```

Build a standalone application:

```bash
make build
```

Clean build files:

```bash
make clean
```

Uninstall Fexus:

```bash
make uninstall
```

## Building Fexus

Fexus can be packaged into a standalone desktop application with PyInstaller.

```bash
make build
```

The build creates the application in:

```text
dist/Fexus
```

The packaged application is intended to let end users run Fexus without setting up a Python environment themselves.

## First launch

Start Fexus and use **Discover** to find devices visible to the local machine.

For a known device, use:

```text
Devices → Add device
```

The **Connect** page can then be used to test a saved device or enter an address manually.

## Connection methods

| Method       | Main use                                      |
| ------------ | --------------------------------------------- |
| SSH          | Linux servers, Raspberry Pis, NAS appliances  |
| HTTP / HTTPS | Routers, dashboards, local APIs               |
| MQTT         | ESP32, ESP8266 and IoT systems                |
| SNMP         | Switches, routers, NAS and network appliances |
| ICMP         | Basic reachability                            |
| TCP          | Service and port checks                       |
| Serial / USB | ESP boards, Pico and embedded hardware        |
| BLE          | Nearby Bluetooth Low Energy devices           |
| RDP          | Windows desktops and servers                  |
| VNC          | Remote graphical systems                      |
| SMB          | NAS and file-server checks                    |
| Wake-on-LAN  | Remote power-on for supported hardware        |

## Setting up connected devices

Detailed setup tutorials are available in the `docs/` directory.

These cover:

* Linux servers
* Raspberry Pi
* Windows systems
* ESP32 / ESP8266
* MQTT
* USB / serial devices
* Bluetooth LE
* Routers
* Switches
* NAS systems
* SNMP
* RDP
* VNC
* SMB
* Wake-on-LAN
* Docker
* libvirt
* Network checks

## SSH

Fexus uses your existing SSH configuration, keys, and SSH agent.

It does not install a Fexus agent on remote machines.

Generate an SSH key when needed:

```bash
ssh-keygen -t ed25519
```

Copy it to a server:

```bash
ssh-copy-id user@192.168.1.20
```

Test normal SSH access before adding the machine to Fexus:

```bash
ssh user@192.168.1.20
```

## MQTT

Install MQTT support:

```bash
python3 -m pip install --user --break-system-packages -e ".[mqtt]"
```

In Fexus:

1. Open **Connect**
2. Select **MQTT**
3. Enter the broker address and port
4. Add credentials when required
5. Test the connection
6. Publish a message when needed

This is useful for ESP32, ESP8266 and other IoT projects.

## SNMP

Install SNMP support:

```bash
python3 -m pip install --user --break-system-packages -e ".[snmp]"
sudo apt install -y snmp
```

Fexus performs read-only system-description checks through Net-SNMP.

## RDP / VNC

Fexus does not embed a remote desktop server.

Instead, it launches an existing client installed on your machine, such as:

* FreeRDP
* Remmina
* another compatible desktop client

## Wake-on-LAN

Add a device with its MAC address and use:

```text
Connect → Wake on LAN
```

The target machine and network must support and have Wake-on-LAN enabled.

## Docker

Install Docker integration:

```bash
python3 -m pip install --user --break-system-packages -e ".[docker]"
```

Fexus reads the local Docker socket and displays container information.

The inventory view is read-only.

## Virtual machines

On Linux systems using libvirt:

```bash
virsh list --all
```

Fexus can read virtual machine names and states through `virsh`.

## NAS and network equipment

Fexus can connect to network equipment and appliances using the protocols they already expose.

Depending on the device, this may include:

* HTTP
* HTTPS
* SNMP
* TCP
* ICMP
* SSH
* SMB

## Discovery

### LAN neighbors

On Linux, Fexus can use the local neighbor table to discover nearby devices without aggressively scanning the entire subnet.

### mDNS

Optional mDNS discovery can locate common local services such as:

* SSH
* HTTP
* HTTPS
* SMB
* MQTT
* printers

Install support with:

```bash
python3 -m pip install --user --break-system-packages -e ".[mdns]"
```

### USB / Serial

Install serial support:

```bash
python3 -m pip install --user --break-system-packages -e ".[serial]"
```

Then connect an ESP32, ESP8266, Raspberry Pi Pico or another serial device over USB.

### Bluetooth LE

Install BLE support:

```bash
python3 -m pip install --user --break-system-packages -e ".[ble]"
```

Fexus will show nearby BLE advertisements when Bluetooth access is available.

## Data and privacy

Fexus stores its local inventory and event history in an SQLite database.

### Linux

```text
~/.local/share/fexus/fexus.db
```

### macOS

```text
~/Library/Application Support/Fexus/fexus.db
```

### Windows

```text
%LOCALAPPDATA%\Fexus\fexus.db
```

Fexus does not require a cloud account.

Device communication happens directly through local or supported network protocols.

## Project structure

```text
fexus/
├── fexus/
│   └── app/
├── tests/
├── docs/
├── assets/
├── .github/
├── Makefile
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

## Development

Fexus is developed as a normal Python project and does not require a repository-local virtual environment.

Install the development dependencies:

```bash
make dev
```

Run the test suite:

```bash
make test
```

Run Ruff:

```bash
make lint
```

Run the application:

```bash
make run
```

Build the desktop application:

```bash
make build
```

## Contributing

Contributions, bug reports, feature requests, documentation improvements, and device integrations are welcome.

Before contributing, read:

* [`CONTRIBUTING.md`](CONTRIBUTING.md)
* [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
* [`SECURITY.md`](SECURITY.md)

For security issues, follow the responsible disclosure process described in [`SECURITY.md`](SECURITY.md).

## License

Fexus is released under the MIT License.

See [`LICENSE`](LICENSE) for the full license text.

## Support

For questions, bugs, feature requests, and integration problems, use the GitHub repository:

https://github.com/filipek805/fexus

## Support the project

Fexus is free to use and open source.

If the project is useful to you, optional donations can help support development, testing hardware, and future integrations.
