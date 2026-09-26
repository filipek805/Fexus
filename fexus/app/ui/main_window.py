from uuid import uuid4

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QProgressBar, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget
)

from ..core.models import Device
from ..core.storage import Storage
from ..integrations.docker import list_local_containers
from ..integrations.libvirt import list_local_vms
from ..integrations.local import collect_local
from ..integrations.network import ping, tcp_probe
from ..integrations.serial import list_serial_devices
from ..integrations.ssh import collect_linux


class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")


class MainWindow(QMainWindow):
    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self.setWindowTitle("Fexus")
        self.resize(1280, 820)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.sidebar())
        self.stack = QStackedWidget()
        self.stack.addWidget(self.overview_page())
        self.stack.addWidget(self.devices_page())
        self.stack.addWidget(self.services_page())
        self.stack.addWidget(self.network_page())
        self.stack.addWidget(self.events_page())
        layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)
        self.refresh()
        QTimer.singleShot(250, self.refresh)

    def sidebar(self):
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(225)
        box = QVBoxLayout(side)
        box.setContentsMargins(18, 24, 18, 18)

        brand = QLabel("FEXUS")
        brand.setObjectName("Brand")
        box.addWidget(brand)
        sub = QLabel("INFRASTRUCTURE CONTROL")
        sub.setObjectName("Muted")
        box.addWidget(sub)
        box.addSpacing(28)

        self.nav_buttons = []
        for index, label in enumerate(["Overview", "Devices", "Services", "Network", "Events"]):
            b = QPushButton(label)
            b.setObjectName("Nav")
            b.setCheckable(True)
            b.clicked.connect(lambda checked=False, i=index: self.switch_page(i))
            box.addWidget(b)
            self.nav_buttons.append(b)

        self.nav_buttons[0].setChecked(True)
        box.addStretch(1)

        status = QLabel("●  LOCAL MODE")
        status.setStyleSheet("color:#78f2c1;")
        box.addWidget(status)
        return side

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, b in enumerate(self.nav_buttons):
            b.setChecked(i == index)
        self.refresh()

    def page(self, title, subtitle):
        page = QWidget()
        box = QVBoxLayout(page)
        box.setContentsMargins(32, 28, 32, 28)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:30px;font-weight:800;")
        box.addWidget(title_label)
        sub = QLabel(subtitle)
        sub.setObjectName("Muted")
        box.addWidget(sub)
        box.addSpacing(22)
        return page, box

    def overview_page(self):
        page, box = self.page("Overview", "Your lab at a glance.")
        self.stats_grid = QGridLayout()
        box.addLayout(self.stats_grid)
        box.addSpacing(14)

        split = QHBoxLayout()
        self.overview_list = QListWidget()
        self.overview_list.setSelectionMode(QAbstractItemView.NoSelection)
        split.addWidget(self.overview_list, 2)

        card = Card()
        cbox = QVBoxLayout(card)
        cbox.addWidget(QLabel("Local machine"))
        self.local_info = QLabel("Collecting…")
        self.local_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        cbox.addWidget(self.local_info)
        split.addWidget(card, 1)
        box.addLayout(split)
        return page

    def devices_page(self):
        page, box = self.page("Devices", "Servers, Raspberry Pis, NAS systems, network gear and embedded hardware.")
        actions = QHBoxLayout()
        self.device_filter = QLineEdit()
        self.device_filter.setPlaceholderText("Search devices")
        self.device_filter.textChanged.connect(self.refresh_devices)
        actions.addWidget(self.device_filter, 1)

        add = QPushButton("Add device")
        add.clicked.connect(self.add_device_dialog)
        actions.addWidget(add)

        remove = QPushButton("Remove selected")
        remove.clicked.connect(self.remove_selected)
        actions.addWidget(remove)
        box.addLayout(actions)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Address", "Status", "Tags", "Last seen"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        box.addWidget(self.table, 1)
        return page

    def services_page(self):
        page, box = self.page("Services", "Containers, virtual machines and serial-connected devices.")
        self.services = QListWidget()
        self.services.setSelectionMode(QAbstractItemView.NoSelection)
        box.addWidget(self.services, 1)
        refresh = QPushButton("Refresh services")
        refresh.clicked.connect(self.refresh_services)
        box.addWidget(refresh)
        return page

    def network_page(self):
        page, box = self.page("Network", "Read-only reachability and TCP service checks.")
        form = QFormLayout()
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.1 or hostname")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("22")
        form.addRow("Host", self.host_input)
        form.addRow("TCP port", self.port_input)
        box.addLayout(form)

        run = QPushButton("Run check")
        run.clicked.connect(self.run_network_check)
        box.addWidget(run)

        self.network_result = QLabel("No check yet.")
        self.network_result.setWordWrap(True)
        self.network_result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        box.addWidget(self.network_result)
        box.addStretch(1)
        return page

    def events_page(self):
        page, box = self.page("Events", "Local activity and connection history.")
        self.events = QListWidget()
        self.events.setSelectionMode(QAbstractItemView.NoSelection)
        box.addWidget(self.events)
        return page

    def make_stat(self, label):
        card = Card()
        box = QVBoxLayout(card)
        a = QLabel(label.upper())
        a.setObjectName("Muted")
        box.addWidget(a)
        value = QLabel("0")
        value.setStyleSheet("font-size:28px;font-weight:800;")
        box.addWidget(value)
        return card, value

    def refresh_overview(self):
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        devices = self.storage.list_devices()
        counts = [
            ("DEVICES", len(devices)),
            ("ONLINE", sum(d.status == "online" for d in devices)),
            ("SERVERS", sum(d.kind in ("server", "raspberry-pi") for d in devices)),
            ("IOT", sum(d.kind == "esp" for d in devices)),
            ("NETWORK", sum(d.kind == "network" for d in devices)),
        ]
        for i, (label, value) in enumerate(counts):
            card, value_label = self.make_stat(label)
            value_label.setText(str(value))
            self.stats_grid.addWidget(card, 0, i)

        self.overview_list.clear()
        if not devices:
            self.overview_list.addItem("No devices yet. Open Devices → Add device.")
        for d in devices[:12]:
            item = QListWidgetItem(f"{d.name}   ·   {d.kind}   ·   {d.status}")
            self.overview_list.addItem(item)

        info = collect_local()
        self.local_info.setText(
            f"Host: {info['hostname']}\n"
            f"Platform: {info['platform']}\n"
            f"CPU: {info['cpu_percent']:.0f}%\n"
            f"Memory: {info['memory_percent']:.0f}%\n"
            f"Disk: {info['disk_percent']:.0f}%\n"
            f"Uptime: {info['uptime_seconds']//3600}h"
        )

    def refresh_devices(self):
        query = self.device_filter.text().lower() if hasattr(self, "device_filter") else ""
        devices = self.storage.list_devices()
        if query:
            devices = [d for d in devices if query in f"{d.name} {d.kind} {d.address}".lower()]
        self.table.setRowCount(len(devices))
        for row, d in enumerate(devices):
            values = [
                d.name, d.kind, d.address, d.status,
                ", ".join(d.tags),
                d.last_seen.isoformat(timespec="minutes") if d.last_seen else "—",
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def refresh_services(self):
        self.services.clear()
        containers = list_local_containers()
        vms = list_local_vms()
        serial = list_serial_devices()

        if not containers and not vms and not serial:
            self.services.addItem("No local Docker containers, libvirt VMs or serial devices found.")

        for c in containers:
            self.services.addItem(f"DOCKER   {c['name']}   ·   {c['image']}   ·   {c['status']}")
        for v in vms:
            self.services.addItem(f"VM       {v['name']}   ·   {v['status']}")
        for s in serial:
            self.services.addItem(f"SERIAL   {s['device']}   ·   {s['description']}")

    def refresh_events(self):
        self.events.clear()
        rows = self.storage.recent_events()
        if not rows:
            self.events.addItem("No events yet.")
        for r in rows:
            self.events.addItem(f"{r['created_at']}   [{r['level']}]   {r['message']}")

    def refresh(self):
        self.refresh_overview()
        self.refresh_devices()
        self.refresh_services()
        self.refresh_events()

    def add_device_dialog(self):
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Add device")
        form = QFormLayout(dialog)

        name = QLineEdit()
        kind = QComboBox()
        kind.addItems(["server", "raspberry-pi", "nas", "network", "esp"])
        address = QLineEdit()
        port = QLineEdit()
        username = QLineEdit()
        tags = QLineEdit()
        tags.setPlaceholderText("core, docker, storage")

        form.addRow("Name", name)
        form.addRow("Type", kind)
        form.addRow("Address", address)
        form.addRow("Port", port)
        form.addRow("SSH username", username)
        form.addRow("Tags", tags)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        device = Device(
            id=str(uuid4()),
            name=name.text().strip() or "Unnamed device",
            kind=kind.currentText(),
            address=address.text().strip(),
            port=int(port.text()) if port.text().strip().isdigit() else None,
            username=username.text().strip(),
            tags=[x.strip() for x in tags.text().split(",") if x.strip()],
        )

        if device.address and device.kind in ("server", "raspberry-pi"):
            result = collect_linux(device.address, device.username, device.port or 22)
            if result.ok:
                device.status = "online"
                device.metadata.update(result.data)
                device.touch()
                self.storage.add_event("info", "ssh", f"Connected to {device.name}")
            else:
                device.status = "offline"
                self.storage.add_event("warning", "ssh", f"{device.name}: {result.error}")
        elif device.address:
            result = ping(device.address)
            device.status = "online" if result["reachable"] else "offline"
            device.touch()
            self.storage.add_event(
                "info" if device.status == "online" else "warning",
                "network",
                f"{device.name}: {device.status}",
            )
        else:
            self.storage.add_event("info", "inventory", f"Added {device.name}")

        self.storage.save_device(device)
        self.refresh()

    def remove_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        name = self.table.item(row, 0).text()
        devices = self.storage.list_devices()
        target = next((d for d in devices if d.name == name), None)
        if not target:
            return
        confirm = QMessageBox.question(
            self, "Remove device", f"Remove '{target.name}' from Fexus?"
        )
        if confirm == QMessageBox.Yes:
            self.storage.delete_device(target.id)
            self.storage.add_event("info", "inventory", f"Removed {target.name}")
            self.refresh()

    def run_network_check(self):
        host = self.host_input.text().strip()
        if not host:
            self.network_result.setText("Enter a host.")
            return
        port_text = self.port_input.text().strip()
        if port_text:
            result = tcp_probe(host, int(port_text))
            self.network_result.setText(
                f"{host}:{port_text}\n"
                f"Reachable: {result.get('reachable')}\n"
                f"Latency: {result.get('latency_ms', '—')} ms\n"
                f"{result.get('error', '')}"
            )
        else:
            result = ping(host)
            self.network_result.setText(f"{host}\nReachable: {result['reachable']}")
