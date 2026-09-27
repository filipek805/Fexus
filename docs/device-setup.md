# Connecting another device to Fexus

Fexus is local-first: the target device does not need a Fexus account, cloud service, or Fexus agent. You enable a protocol that the device already supports, make sure Fexus can reach it, and then add it under **Devices** or test it under **Connect**.

## Before you add anything

1. Put the Fexus computer and the target device on a network where they can reach each other.
2. Give the target a stable hostname or DHCP reservation when possible.
3. Enable the service on the target device.
4. Allow the service through the target device's firewall.
5. Test from the Fexus computer with the normal client first.
6. Add the same address, port, username and protocol in Fexus.

Do not expose management ports directly to the public internet just to make Fexus connect. Prefer your LAN or a private VPN such as WireGuard/Tailscale.

---

## 1. Linux server / Raspberry Pi over SSH

### On the target

Debian, Ubuntu and Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

Check it:

```bash
systemctl status ssh --no-pager
hostname -I
```

If UFW is enabled:

```bash
sudo ufw allow OpenSSH
```

From the Fexus computer, test normal SSH first:

```bash
ssh user@192.168.1.20
```

For key-based authentication:

```bash
ssh-keygen -t ed25519
ssh-copy-id user@192.168.1.20
```

### In Fexus

Add a device with:

```text
Protocol: SSH
Address: 192.168.1.20
Port: 22
Username: user
```

Fexus uses the system SSH known-hosts database for host verification. Connect with `ssh` once first so the host key is known and trusted.

---

## 2. Windows over SSH

On the Windows target, open PowerShell as Administrator:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

Allow TCP 22 if Windows Firewall does not create the rule automatically:

```powershell
New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

Then test from Fexus:

```bash
ssh windows-user@192.168.1.30
```

Use the same address, port and username in Fexus.

---

## 3. ESP32 / ESP8266 over MQTT

Fexus does not talk directly to an ESP over MQTT unless an MQTT broker is available. The usual layout is:

```text
ESP32 / ESP8266  --->  MQTT broker  <---  Fexus
```

### Set up a broker

For a Linux machine, Mosquitto is a simple option:

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

For a LAN-only setup, configure the broker to listen on the LAN interface and use authentication. A typical Mosquitto configuration can contain:

```text
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Create a broker account with:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd fexus
sudo systemctl restart mosquitto
```

### Test the broker

On the broker machine:

```bash
mosquitto_sub -h 127.0.0.1 -t 'home/fexus/#' -u fexus -P 'YOUR_PASSWORD'
```

From another terminal:

```bash
mosquitto_pub -h BROKER_IP -t 'home/fexus/test' -m 'hello' -u fexus -P 'YOUR_PASSWORD'
```

### On the ESP

Configure the ESP to join the same LAN and connect to the broker's IP/hostname. Publish or subscribe to the topics you want to use.

For example:

```text
Broker: 192.168.1.40
Port: 1883
Topic: home/esp01/status
```

### In Fexus

Install MQTT support:

```bash
pip install -e ".[mqtt]"
```

Then use:

```text
Protocol: MQTT
Address: 192.168.1.40
Port: 1883
Username: fexus
Secret: broker password
```

You can use **Publish MQTT** to send a test message.

For internet-exposed MQTT, use a TLS listener rather than plain port 1883 and restrict access with the broker firewall.

---

## 4. ESP32 / ESP8266 / Pico over USB serial

Connect the board to the Fexus computer with USB.

Install serial support:

```bash
pip install -e ".[serial]"
```

Then open **Discover → USB / Serial**.

On Linux, check the device manually:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

If the device exists but your normal user cannot open it, add the user to the `dialout` group:

```bash
sudo usermod -aG dialout "$USER"
```

Log out and back in afterward.

Fexus currently discovers serial devices and records their port, VID/PID and manufacturer. A serial monitor or protocol-specific control layer can be added later without changing the discovery system.

---

## 5. Bluetooth LE device

### On the target

The target must actually advertise over BLE. Examples include sensors, beacons and ESP32 BLE applications.

The Fexus computer needs Bluetooth enabled and working.

Install BLE support:

```bash
pip install -e ".[ble]"
```

On Linux, make sure the Bluetooth service is running:

```bash
systemctl status bluetooth --no-pager
```

Then use **Discover → Bluetooth LE**.

Fexus discovers BLE advertisements. Discovery does not automatically mean that every BLE device can be controlled; device-specific GATT support is required for active control.

---

## 6. Router, switch, access point or NAS over HTTP / HTTPS

Enable the device's web management interface or local API.

Typical examples:

```text
Router: https://192.168.1.1
NAS:    https://192.168.1.50
AP:     http://192.168.1.2
```

Make sure the management interface listens on the LAN and that the target firewall allows the management port.

Fexus performs a read-only GET health check. It does not need the device's web password for a basic reachability check.

Add it in Fexus with the HTTP or HTTPS protocol and the management port.

---

## 7. Router / switch / NAS over SNMP

SNMP must be enabled on the target device. Prefer a read-only account/community and restrict SNMP to the Fexus host or management VLAN.

Fexus currently performs an SNMPv2c `sysDescr` query.

### On the Fexus computer

Debian/Ubuntu:

```bash
sudo apt install -y snmp
```

### On the target

Enable SNMP in the device's management UI and note:

```text
SNMP version: v2c
Read community: YOUR_READ_COMMUNITY
Port: 161/UDP
```

Then in Fexus:

```text
Protocol: SNMP
Address: 192.168.1.2
Port: 161
Secret: YOUR_READ_COMMUNITY
```

Do not use a writable SNMP community when a read-only option is available.

---

## 8. Windows / Linux desktop over RDP

Fexus launches an RDP client; the target still needs to provide RDP.

### Windows target

Enable **Remote Desktop** in Windows settings and allow the Windows firewall rule for Remote Desktop. Make sure the target edition supports hosting RDP.

Install a client on the Fexus computer, for example Remmina or FreeRDP.

Then add:

```text
Protocol: RDP
Address: 192.168.1.30
Port: 3389
Username: user
```

Fexus opens the external client rather than implementing RDP itself.

---

## 9. Linux / NAS / VM over VNC

The target needs a VNC server and a listening port, commonly 5900.

Install a VNC client on the Fexus computer, then add:

```text
Protocol: VNC
Address: 192.168.1.40
Port: 5900
```

Use an encrypted/private network for VNC unless your VNC stack provides secure transport.

---

## 10. NAS / file server over SMB

SMB is currently used as a network service check. The target should expose SMB on TCP 445.

On Linux/Samba:

```bash
sudo apt install -y samba
sudo systemctl enable --now smbd
```

Verify from the Fexus computer:

```bash
nc -vz 192.168.1.50 445
```

Then add the device using the SMB protocol and port 445.

Fexus's current SMB connector verifies service reachability; it does not yet provide a full file-browser UI.

---

## 11. Wake-on-LAN

Wake-on-LAN is configured on the target machine, not inside Fexus.

### Target requirements

Enable Wake-on-LAN in:

- BIOS/UEFI, if the system provides the option
- the operating system's network adapter settings
- the network adapter's power-management settings

The machine must remain connected to power and normally needs wired Ethernet for reliable WoL.

Find the MAC address, for example:

```bash
ip link
```

Then store the MAC in Fexus and use **Wake on LAN**.

---

## 12. Docker

Fexus's current Docker integration is for the Docker environment available on the Fexus host. Install the optional SDK:

```bash
pip install -e ".[docker]"
```

Then make sure the Fexus user can access Docker:

```bash
docker ps
```

For a remote Docker host, use SSH to manage the remote machine rather than exposing the unauthenticated Docker TCP socket. Remote Docker socket exposure can grant root-equivalent control of the host.

---

## 13. libvirt / KVM virtual machines

Fexus reads local libvirt inventory through `virsh`.

On the Fexus Linux host:

```bash
virsh list --all
```

If your user cannot access the libvirt daemon, configure normal libvirt permissions/groups for your distribution. VMs can then be discovered from the local host.

For a VM that lives on another physical host, connect to that host over SSH and use the VM's own SSH/RDP/VNC service for remote access.

---

## 14. ICMP and TCP checks

Nothing special needs to be installed on a target for basic checks.

The target must simply be reachable and allow the traffic you are testing.

Examples:

```text
ICMP → 192.168.1.50
TCP  → 192.168.1.50:22
TCP  → 192.168.1.50:443
```

Use TCP checks when you care about a particular service rather than only whether the host responds to ping.

---

## Troubleshooting

### Fexus says the device is offline

From the Fexus computer:

```bash
ping DEVICE_IP
```

Then test the actual service port:

```bash
nc -vz DEVICE_IP PORT
```

For SSH:

```bash
ssh USER@DEVICE_IP
```

### The device appears in discovery but will not connect

Discovery and connectivity are separate. A device can advertise an mDNS service or appear in the neighbor table while its firewall blocks the service itself.

Check the target's service, firewall and listening port.

### Fexus sees my ESP over USB but I cannot use it

That means serial discovery is working. Fexus currently identifies the serial device; a board-specific serial protocol is still required for active control.

### MQTT works locally but not from Fexus

Check:

1. The broker is listening on the LAN address, not only `127.0.0.1`.
2. TCP 1883 or your configured TLS port is allowed by the broker host firewall.
3. The username/password is correct.
4. The ESP and Fexus computer can reach the broker address.
5. The broker ACL permits the topic you are publishing to.

### SNMP fails

Check UDP 161, the SNMP version, and the read community. Also confirm that the device allows SNMP from the Fexus host.
