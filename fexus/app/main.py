import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .core.storage import Storage
from .ui.main_window import MainWindow
from .ui.theme import DARK


def data_path() -> Path:
    root = Path.home() / ".local" / "share" / "fexus"
    if sys.platform.startswith("win"):
        root = Path.home() / "AppData" / "Local" / "Fexus"
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support" / "Fexus"
    root.mkdir(parents=True, exist_ok=True)
    return root / "fexus.db"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Fexus")
    app.setOrganizationName("Fexus")
    app.setStyleSheet(DARK)

    storage = Storage(data_path())
    window = MainWindow(storage)
    window.show()

    code = app.exec()
    storage.close()
    raise SystemExit(code)


if __name__ == "__main__":
    main()
