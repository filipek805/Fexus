.PHONY: install dev test lint run build clean uninstall

PYTHON := python3
PIP := $(PYTHON) -m pip

install:
	$(PIP) install --user --break-system-packages -e .

dev:
	$(PIP) install --user --break-system-packages -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

run:
	$(PYTHON) -m fexus.app

build:
	$(PIP) install --user --break-system-packages pyinstaller
	pyinstaller --noconfirm --clean --windowed \
		--name Fexus \
		--collect-all PySide6 \
		fexus/app/main.py

clean:
	rm -rf build dist *.spec

uninstall:
	$(PIP) uninstall -y fexus
