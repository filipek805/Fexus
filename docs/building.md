# Building Fexus

## Development

Fexus does not require a repository-local virtual environment. Install development dependencies into the user Python environment:

```bash
python3 -m pip install --user --break-system-packages -e ".[dev]"
```

Then run:

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m fexus
```

The Makefile provides the same commands:

```bash
make dev
make test
make lint
make run
```

## Linux desktop launcher

```bash
make install
```

This installs the user-level application launcher and, when `~/Desktop` exists, a desktop shortcut.

## Standalone application

Build with PyInstaller through the Makefile:

```bash
make build
```

The one-file executable appears at:

```text
dist/Fexus
```

To install that executable and update the desktop launcher:

```bash
make install-app
```

The installed standalone binary is:

```text
~/.local/share/fexus/Fexus
```

The PyInstaller entry point is `packaging/fexus_launcher.py`, which imports the real Fexus package entry point.
