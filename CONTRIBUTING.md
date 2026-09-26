# Contributing to Fexus

Fexus is a free, open-source project and contributions are welcome.

## Development setup

```bash
git clone https://github.com/filipek805/fexus.git
cd fexus
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run Fexus:

```bash
fexus
```

## Before opening an issue

Search existing issues first.

For bugs, include:

- Fexus version
- operating system
- Python version
- device type
- reproduction steps
- relevant logs

Never post:

- passwords
- SSH private keys
- API tokens
- SNMP credentials
- private IP information that would compromise your network

## Pull requests

Keep pull requests focused.

Please:

- add tests for behavior changes
- update docs when needed
- avoid unrelated formatting changes
- explain security implications for network features
- avoid adding hidden telemetry

## New integrations

A new integration should:

1. be isolated in `fexus/app/integrations/`
2. fail gracefully if its dependency is missing
3. default to read-only behavior
4. avoid blocking the UI thread
5. include tests where practical
6. document required permissions

## Design principles

Fexus is:

- local-first
- free
- open source
- explicit about network access
- read-only by default

Features that modify external systems should require deliberate user interaction and clear confirmation.
