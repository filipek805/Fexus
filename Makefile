PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

XDG_DATA_HOME ?= $(HOME)/.local/share
APP_DATA_DIR := $(XDG_DATA_HOME)/fexus
APP_DIR := $(XDG_DATA_HOME)/applications
ICON_DIR := $(XDG_DATA_HOME)/icons/hicolor/scalable/apps
DESKTOP_DIR ?= $(HOME)/Desktop
DESKTOP_FILE := $(APP_DIR)/fexus.desktop
DESKTOP_SHORTCUT := $(DESKTOP_DIR)/Fexus.desktop

PIP_FLAGS ?= --user --break-system-packages

.PHONY: install install-desktop install-app dev test lint run build clean uninstall

install:
	$(PIP) install $(PIP_FLAGS) -e .
	$(MAKE) install-desktop
	@echo
	@echo "Fexus is installed without a virtual environment."
	@echo "Run it with: make run"
	@echo "Desktop launcher: $(DESKTOP_FILE)"
	@if [ -d "$(DESKTOP_DIR)" ]; then echo "Desktop shortcut: $(DESKTOP_SHORTCUT)"; fi
	@if ! echo "$(PATH)" | tr ':' '\\n' | grep -Fxq "$(HOME)/.local/bin"; then \
		echo "Note: $(HOME)/.local/bin is not currently on PATH; use 'python3 -m fexus' or add it to PATH."; \
	fi

install-desktop:
	mkdir -p "$(APP_DIR)" "$(ICON_DIR)"
	install -m 644 packaging/linux/fexus.desktop "$(DESKTOP_FILE)"
	install -m 644 assets/fexus-mark.svg "$(ICON_DIR)/fexus.svg"
	@if [ -d "$(DESKTOP_DIR)" ]; then \
		install -m 755 packaging/linux/fexus.desktop "$(DESKTOP_SHORTCUT)"; \
		if command -v gio >/dev/null 2>&1; then gio set "$(DESKTOP_SHORTCUT)" metadata::trusted true 2>/dev/null || true; fi; \
	fi
	@if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(APP_DIR)" >/dev/null 2>&1 || true; fi

install-app: build
	mkdir -p "$(APP_DATA_DIR)" "$(APP_DIR)" "$(ICON_DIR)"
	install -m 755 dist/Fexus "$(APP_DATA_DIR)/Fexus"
	install -m 644 assets/fexus-mark.svg "$(ICON_DIR)/fexus.svg"
	sed 's|^Exec=.*|Exec=$(APP_DATA_DIR)/Fexus|' packaging/linux/fexus.desktop > "$(DESKTOP_FILE)"
	chmod 644 "$(DESKTOP_FILE)"
	@if [ -d "$(DESKTOP_DIR)" ]; then \
		install -m 755 "$(DESKTOP_FILE)" "$(DESKTOP_SHORTCUT)"; \
		if command -v gio >/dev/null 2>&1; then gio set "$(DESKTOP_SHORTCUT)" metadata::trusted true 2>/dev/null || true; fi; \
	fi
	@if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(APP_DIR)" >/dev/null 2>&1 || true; fi
	@echo "Standalone Fexus installed to $(APP_DATA_DIR)/Fexus"


dev:
	$(PIP) install $(PIP_FLAGS) -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

run:
	$(PYTHON) -m fexus

build:
	$(PIP) install $(PIP_FLAGS) pyinstaller
	$(PYTHON) -m PyInstaller --noconfirm --clean --onefile --windowed \
		--name Fexus \
		--collect-all PySide6 \
		packaging/fexus_launcher.py

clean:
	rm -rf build dist *.spec .pytest_cache .ruff_cache

uninstall:
	$(PIP) uninstall -y fexus || true
	rm -f "$(DESKTOP_FILE)" "$(DESKTOP_SHORTCUT)" "$(ICON_DIR)/fexus.svg"
	rm -rf "$(APP_DATA_DIR)"
	@if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(APP_DIR)" >/dev/null 2>&1 || true; fi
