.PHONY: install dev test lint run build

install:
	python3 -m pip install -e .

dev:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest

lint:
	python3 -m ruff check .

run:
	python3 -m fexus.app

build:
	python3 -m pip install pyinstaller
	pyinstaller --noconfirm --clean --windowed --name Fexus --collect-all PySide6 fexus/app/main.py
