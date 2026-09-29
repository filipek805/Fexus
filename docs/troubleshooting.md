# Troubleshooting

## Fexus does not start

Check Python:

```bash
python3 --version
```

Reinstall:

```bash
python3 -m pip install --user --break-system-packages -e .
```

Try:

```bash
python3 -m fexus
```

## SSH device is offline

First test SSH manually:

```bash
ssh user@host
```

Check:

- hostname/IP
- username
- port
- firewall
- SSH service
- SSH keys

## Docker is not detected

Check:

```bash
docker ps
```

Then install:

```bash
python3 -m pip install --user --break-system-packages -e ".[docker]"
```

On Linux, make sure your user can access Docker.

## VMs are missing

Check:

```bash
virsh list --all
```

If `virsh` is missing, install your distribution's libvirt client package.

## Serial devices are missing

Install:

```bash
python3 -m pip install --user --break-system-packages -e ".[serial]"
```

Then restart Fexus and reconnect the board.

## Reset Fexus

Delete the local SQLite database.

Linux:

```bash
rm ~/.local/share/fexus/fexus.db
```

The next launch starts with an empty inventory.
