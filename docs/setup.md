# Fexus setup

Fexus is a native desktop application.

You do **not** deploy a web server.

## 1. Install Python

Use Python 3.11 or newer.

Check:

```bash
python3 --version
```

## 2. Download Fexus

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus
```

## 3. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 4. Install Fexus

```bash
pip install -e .
```

For optional integrations:

```bash
pip install -e ".[docker,serial,snmp]"
```

## 5. Launch

```bash
fexus
```

Or:

```bash
python -m fexus.app
```

A Fexus application window should open.

## 6. Add a server

Open:

```text
Devices → Add device
```

Example:

```text
Name: Main Server
Type: server
Address: 192.168.1.20
Port: 22
SSH username: filip
Tags: server, docker
```

Fexus attempts a read-only SSH collection.

### Recommended SSH setup

On the Fexus computer:

```bash
ssh-keygen -t ed25519
```

Copy the key:

```bash
ssh-copy-id filip@192.168.1.20
```

Confirm:

```bash
ssh filip@192.168.1.20
```

Once normal SSH works, Fexus can usually use the same connection.

## 7. Add a Raspberry Pi

The process is the same.

Set:

```text
Type: raspberry-pi
Address: raspberrypi.local
Username: pi
```

Use the current username for your Pi distribution.

## 8. Add a NAS

Use the NAS hostname or IP.

For example:

```text
Type: NAS
Address: 192.168.1.40
```

Fexus can perform basic reachability checks.

## 9. Add network equipment

Use:

```text
Type: network
Address: 192.168.1.1
```

The Network page can also run manual reachability and TCP checks.

## 10. ESP devices

Connect an ESP32/ESP8266 to USB.

Open:

```text
Services
```

Fexus checks serial ports and lists detected devices.

Optional serial support:

```bash
pip install pyserial
```

For advanced telemetry, use the plugin/integration system described in `docs/integrations.md`.

## 11. Docker

Install the Docker Python integration:

```bash
pip install -e ".[docker]"
```

Then start Docker normally.

Fexus checks the local Docker socket using the official Docker SDK.

## 12. Virtual machines

On a Linux host with libvirt:

```bash
virsh list --all
```

Fexus uses the same command to discover local VMs.

## 13. Where data is stored

Linux:

```text
~/.local/share/fexus/fexus.db
```

macOS:

```text
~/Library/Application Support/Fexus/fexus.db
```

Windows:

```text
%LOCALAPPDATA%\Fexus\fexus.db
```

Delete the database to reset the application.

## 14. No account or cloud

Fexus does not need:

- a Fexus login
- an internet connection
- a cloud server
- an API key
- a subscription

Internet access is only useful for installing dependencies or updating the software.

## 15. Package Fexus for friends

See `docs/building.md`.
