# Building Fexus

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## PyInstaller

Install:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --noconfirm --clean --windowed \
  --name Fexus \
  --collect-all PySide6 \
  fexus/app/main.py
```

The executable appears under:

```text
dist/Fexus/
```

A future release can add native packaging metadata for:

- AppImage
- Flatpak
- Windows installer
- macOS app bundle
