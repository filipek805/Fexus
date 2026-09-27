from uuid import uuid4

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ..core.connectors import run_connection_test
from ..core.models import Device
from ..core.storage import Storage
from ..integrations.ble import list_ble_devices
from ..integrations.discovery import discover_mdns, discover_neighbors
from ..integrations.docker import list_local_containers
from ..integrations.libvirt import list_local_vms
from ..integrations.local import collect_local
from ..integrations.mqtt import publish
from ..integrations.network import ping, tcp_probe
from ..integrations.remote import launch_remote
from ..integrations.serial import list_serial_devices
from ..integrations.wol import wake_on_lan


class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")


CONNECTIONS = [
    "auto", "ssh", "http", "https", "mqtt", "snmp", "ping", "tcp",
    "serial", "ble", "smb", "rdp", "vnc",
]


class MainWindow(QMainWindow):
    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self.discovery_results = []
        self.setWindowTitle("Fexus")
        self.resize(1320, 860)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.sidebar())
        self.stack = QStackedWidget()
        self.stack.addWidget(self.overview_page())
        self.stack.addWidget(self.devices_page())
        self.stack.addWidget(self.connect_page())
        self.stack.addWidget(self.discovery_page())
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
        side.setFixedWidth(235)
        box = QVBoxLayout(side)
        box.setContentsMargins(18, 24, 18, 18)

        brand = QLabel("FEXUS")
        brand.setObjectName("Brand")
        box.addWidget(brand)
        sub = QLabel("INFRASTRUCTURE CONTROL")
        sub.setObjectName("Muted")
        box.addWidget(sub)
        box.addSpacing(26)

        labels = ["Overview", "Devices", "Connect", "Discover", "Services", "Network", "Events"]
        self.nav_buttons = []
        for index, label in enumerate(labels):
            b = QPushButton(label)
            b.setObjectName("Nav")
            b.setCheckable(True)
            b.clicked.connect(lambda checked=False, i=index: self.switch_page(i))
            box.addWidget(b)
            self.nav_buttons.append(b)

        self.nav_buttons[0].setChecked(True)
        box.addStretch(1)

        status = QLabel("●  LOCAL-FIRST MODE")
        status.setStyleSheet("color:#78f2c1;")
        box.addWidget(status)
        version = QLabel("Fexus 0.3.0")
        version.setObjectName("Muted")
        box.addWidget(version)
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
        box.addSpacing(20)
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
        page, box = self.page(
            "Devices",
            "Servers, Raspberry Pis, NAS systems, network gear, embedded boards and everything around them.",
        )
        actions = QHBoxLayout()
        self.device_filter = QLineEdit()
        self.device_filter.setPlaceholderText("Search devices, addresses or protocols")
        self.device_filter.textChanged.connect(self.refresh_devices)
        actions.addWidget(self.device_filter, 1)

        connect = QPushButton("Connect")
        connect.clicked.connect(self.connect_selected_device)
        actions.addWidget(connect)

        add = QPushButton("Add device")
        add.clicked.connect(self.add_device_dialog)
        actions.addWidget(add)

        remove = QPushButton("Remove selected")
        remove.clicked.connect(self.remove_selected)
        actions.addWidget(remove)
        box.addLayout(actions)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Type", "Connection", "Address", "Status", "MAC", "Last seen"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(lambda index: self.connect_selected_device())
        box.addWidget(self.table, 1)
        return page

    def connect_page(self):
        page, box = self.page(
            "Connect",
            "Test protocols, open remote clients, send MQTT messages and wake machines without leaving Fexus.",
        )
        form = QFormLayout()
        self.connect_device_combo = QComboBox()
        self.connect_device_combo.currentIndexChanged.connect(self.load_connect_device)
        form.addRow("Device", self.connect_device_combo)

        self.connect_method = QComboBox()
        self.connect_method.addItems(CONNECTIONS)
        form.addRow("Protocol", self.connect_method)

        self.connect_address = QLineEdit()
        form.addRow("Address", self.connect_address)

        self.connect_port = QLineEdit()
        form.addRow("Port", self.connect_port)

        self.connect_username = QLineEdit()
        form.addRow("Username", self.connect_username)

        self.connect_secret = QLineEdit()
        self.connect_secret.setEchoMode(QLineEdit.Password)
        self.connect_secret.setPlaceholderText("SNMP community / MQTT password")
        form.addRow("Secret", self.connect_secret)

        self.mqtt_topic = QLineEdit()
        self.mqtt_topic.setPlaceholderText("home/fexus/test")
        form.addRow("MQTT topic", self.mqtt_topic)

        self.mqtt_payload = QLineEdit()
        self.mqtt_payload.setPlaceholderText("Hello from Fexus")
        form.addRow("MQTT payload", self.mqtt_payload)
        box.addLayout(form)

        actions = QHBoxLayout()
        test = QPushButton("Test connection")
        test.clicked.connect(self.test_connection_page)
        actions.addWidget(test)

        mqtt = QPushButton("Publish MQTT")
        mqtt.clicked.connect(self.publish_mqtt)
        actions.addWidget(mqtt)

        self.remote_button = QPushButton("Open remote client")
        self.remote_button.clicked.connect(self.open_remote_client)
        actions.addWidget(self.remote_button)

        wake = QPushButton("Wake on LAN")
        wake.clicked.connect(self.wake_selected)
        actions.addWidget(wake)
        box.addLayout(actions)

        self.connect_result = QLabel("Select a device or enter an address.")
        self.connect_result.setWordWrap(True)
        self.connect_result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        box.addWidget(self.connect_result)
        box.addStretch(1)
        return page

    def discovery_page(self):
        page, box = self.page(
            "Discover",
            "Find devices already visible on your LAN, mDNS services, USB serial hardware and nearby BLE devices.",
        )
        actions = QHBoxLayout()
        for label, handler in [
            ("LAN neighbors", self.discover_lan),
            ("mDNS", self.discover_mdns),
            ("USB / Serial", self.discover_serial),
            ("Bluetooth LE", self.discover_ble),
        ]:
            button = QPushButton(label)
            button.clicked.connect(handler)
            actions.addWidget(button)
        add = QPushButton("Add selected")
        add.clicked.connect(self.add_discovered)
        actions.addWidget(add)
        box.addLayout(actions)

        self.discovery_table = QTableWidget(0, 6)
        self.discovery_table.setHorizontalHeaderLabels(
            ["Name", "Address", "Port", "Type", "Source", "Details"]
        )
        self.discovery_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.discovery_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.discovery_table.setSelectionMode(QAbstractItemView.SingleSelection)
        box.addWidget(self.discovery_table, 1)

        self.discovery_status = QLabel("Run a discovery action to populate this list.")
        self.discovery_status.setObjectName("Muted")
        box.addWidget(self.discovery_status)
        return page

    def services_page(self):
        page, box = self.page(
            "Services",
            "Containers, virtual machines, serial devices and optional local network clients.",
        )
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
            ("IOT", sum(d.kind in ("esp", "bluetooth", "iot") for d in devices)),
            ("NETWORK", sum(d.kind == "network" for d in devices)),
            ("PROTOCOLS", len({(d.connection or "auto") for d in devices})),
        ]
        for i, (label, value) in enumerate(counts):
            card, value_label = self.make_stat(label)
            value_label.setText(str(value))
            self.stats_grid.addWidget(card, 0, i)

        self.overview_list.clear()
        if not devices:
            self.overview_list.addItem("No devices yet. Use Discover or Devices → Add device.")
        for d in devices[:12]:
            item = QListWidgetItem(f"{d.name}   ·   {d.connection}   ·   {d.status}")
            self.overview_list.addItem(item)

        info = collect_local()
        self.local_info.setText(
            f"Host: {info['hostname']}\n"
            f"Platform: {info['platform']}\n"
            f"CPU: {info['cpu_percent']:.0f}%\n"
            f"Memory: {info['memory_percent']:.0f}%\n"
            f"Disk: {info['disk_percent']:.0f}%\n"
            f"Uptime: {info['uptime_seconds']//3600}h\n"
            f"User: {info['user']}"
        )

    def refresh_devices(self):
        query = self.device_filter.text().lower() if hasattr(self, "device_filter") else ""
        devices = self.storage.list_devices()
        if query:
            devices = [
                d for d in devices
                if query in f"{d.name} {d.kind} {d.address} {d.connection} {' '.join(d.tags)}".lower()
            ]
        self.table.setRowCount(len(devices))
        for row, d in enumerate(devices):
            values = [
                d.name,
                d.kind,
                d.connection,
                d.address,
                d.status,
                d.metadata.get("mac", "—"),
                d.last_seen.isoformat(timespec="minutes") if d.last_seen else "—",
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def refresh_connect_devices(self):
        devices = self.storage.list_devices()
        current_id = self.connect_device_combo.currentData() if hasattr(self, "connect_device_combo") else None
        self.connect_device_combo.blockSignals(True)
        self.connect_device_combo.clear()
        self.connect_device_combo.addItem("Manual address", None)
        for device in devices:
            self.connect_device_combo.addItem(
                f"{device.name} · {device.address or 'no address'}", device.id
            )
        index = self.connect_device_combo.findData(current_id)
        self.connect_device_combo.setCurrentIndex(index if index >= 0 else 0)
        self.connect_device_combo.blockSignals(False)
        self.load_connect_device()

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
            detail = s['description'] or s['manufacturer'] or "serial device"
            self.services.addItem(f"SERIAL   {s['device']}   ·   {detail}")

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
        self.refresh_connect_devices()
        self.refresh_services()
        self.refresh_events()

    def add_device_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add device")
        form = QFormLayout(dialog)

        name = QLineEdit()
        kind = QComboBox()
        kind.addItems(["server", "raspberry-pi", "nas", "network", "esp", "iot", "bluetooth", "desktop", "vm"])
        address = QLineEdit()
        port = QLineEdit()
        username = QLineEdit()
        connection = QComboBox()
        connection.addItems(CONNECTIONS)
        mac = QLineEdit()
        tags = QLineEdit()
        tags.setPlaceholderText("core, docker, storage")

        form.addRow("Name", name)
        form.addRow("Type", kind)
        form.addRow("Connection", connection)
        form.addRow("Address", address)
        form.addRow("Port", port)
        form.addRow("SSH username", username)
        form.addRow("MAC address", mac)
        form.addRow("Tags", tags)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        metadata = {}
        if mac.text().strip():
            metadata["mac"] = mac.text().strip()
        device = Device(
            id=str(uuid4()),
            name=name.text().strip() or "Unnamed device",
            kind=kind.currentText(),
            address=address.text().strip(),
            port=int(port.text()) if port.text().strip().isdigit() else None,
            username=username.text().strip(),
            connection=connection.currentText(),
            tags=[x.strip() for x in tags.text().split(",") if x.strip()],
            metadata=metadata,
        )

        if device.address:
            result = run_connection_test(device)
            device.status = "online" if result.ok else "offline"
            device.touch() if result.ok else None
            if result.data:
                device.metadata.update({k: v for k, v in result.data.items() if k in ("hostname", "sysdescr", "status", "latency_ms")})
            self.storage.add_event(
                "info" if result.ok else "warning",
                result.label.lower(),
                f"{device.name}: {result.details.splitlines()[0]}",
            )
        else:
            self.storage.add_event("info", "inventory", f"Added {device.name}")
        self.storage.save_device(device)
        self.refresh()

    def connect_selected_device(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.switch_page(2)
            return
        name = self.table.item(rows[0].row(), 0).text()
        device = next((d for d in self.storage.list_devices() if d.name == name), None)
        if not device:
            return
        self.switch_page(2)
        index = self.connect_device_combo.findData(device.id)
        if index >= 0:
            self.connect_device_combo.setCurrentIndex(index)
        self.test_connection_page()

    def load_connect_device(self):
        device_id = self.connect_device_combo.currentData() if hasattr(self, "connect_device_combo") else None
        if not device_id:
            return
        device = next((d for d in self.storage.list_devices() if d.id == device_id), None)
        if not device:
            return
        self.connect_address.setText(device.address)
        self.connect_method.setCurrentText(device.connection or "auto")
        self.connect_port.setText(str(device.port) if device.port else "")
        self.connect_username.setText(device.username)
        self.connect_secret.clear()

    def _build_connect_device(self):
        device_id = self.connect_device_combo.currentData()
        stored = next((d for d in self.storage.list_devices() if d.id == device_id), None) if device_id else None
        if stored:
            stored.address = self.connect_address.text().strip() or stored.address
            stored.port = int(self.connect_port.text()) if self.connect_port.text().strip().isdigit() else stored.port
            stored.username = self.connect_username.text().strip() or stored.username
            stored.connection = self.connect_method.currentText()
            if self.connect_secret.text():
                stored.metadata["snmp_community"] = self.connect_secret.text()
            return stored
        return Device(
            id="manual",
            name="Manual connection",
            kind="network",
            address=self.connect_address.text().strip(),
            port=int(self.connect_port.text()) if self.connect_port.text().strip().isdigit() else None,
            username=self.connect_username.text().strip(),
            connection=self.connect_method.currentText(),
        )

    def test_connection_page(self):
        device = self._build_connect_device()
        if not device.address:
            self.connect_result.setText("Enter an address first.")
            return
        result = run_connection_test(device)
        self.connect_result.setText(f"{result.label}: {'CONNECTED' if result.ok else 'FAILED'}\n{result.details}")
        if device.id != "manual":
            device.status = "online" if result.ok else "offline"
            if result.ok:
                device.touch()
            self.storage.save_device(device)
            self.storage.add_event(
                "info" if result.ok else "warning",
                result.label.lower(),
                f"{device.name}: {'connected' if result.ok else result.details.splitlines()[0]}",
            )
            self.refresh()

    def publish_mqtt(self):
        device = self._build_connect_device()
        if self.connect_method.currentText() != "mqtt":
            self.connect_result.setText("Select MQTT first.")
            return
        if not device.address or not self.mqtt_topic.text().strip():
            self.connect_result.setText("Enter an MQTT broker address and topic.")
            return
        result = publish(
            self.mqtt_topic.text().strip(),
            self.mqtt_payload.text(),
            device.address,
            device.port or 1883,
            device.username,
            self.connect_secret.text(),
        )
        self.connect_result.setText(
            "MQTT publish succeeded." if result.get("ok") else f"MQTT publish failed: {result.get('error', 'unknown error')}"
        )
        if device.id != "manual":
            self.storage.add_event(
                "info" if result.get("ok") else "warning",
                "mqtt",
                f"{device.name}: MQTT publish to {self.mqtt_topic.text().strip()}",
            )

    def open_remote_client(self):
        method = self.connect_method.currentText()
        if method not in ("rdp", "vnc"):
            self.connect_result.setText("Select RDP or VNC first.")
            return
        address = self.connect_address.text().strip()
        port = int(self.connect_port.text()) if self.connect_port.text().strip().isdigit() else None
        result = launch_remote(method, address, port, self.connect_username.text().strip())
        self.connect_result.setText(result.get("command") or result.get("error", "Done."))

    def wake_selected(self):
        device_id = self.connect_device_combo.currentData()
        device = next((d for d in self.storage.list_devices() if d.id == device_id), None)
        mac = device.metadata.get("mac", "") if device else ""
        if not mac:
            self.connect_result.setText("The selected device has no MAC address. Add one in Devices.")
            return
        result = wake_on_lan(mac)
        self.connect_result.setText(
            f"Wake-on-LAN sent to {mac}." if result.get("ok") else f"Wake-on-LAN failed: {result.get('error')}"
        )

    def _set_discovery(self, items, label):
        self.discovery_results = items
        self.discovery_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                item.get("name", "Unknown"),
                item.get("address", ""),
                item.get("port", "—"),
                item.get("kind", "network"),
                item.get("source", ""),
                item.get("detail", ""),
            ]
            for col, value in enumerate(values):
                self.discovery_table.setItem(row, col, QTableWidgetItem(str(value)))
        self.discovery_status.setText(f"{len(items)} results · {label}")

    def discover_lan(self):
        self._set_discovery(discover_neighbors(), "LAN neighbors")

    def discover_mdns(self):
        results = discover_mdns()
        if not results:
            self.discovery_status.setText("No mDNS results. Install optional zeroconf support with: pip install -e '.[mdns]'")
        self._set_discovery(results, "mDNS")

    def discover_serial(self):
        results = []
        for port in list_serial_devices():
            results.append({
                "name": port["description"] or port["device"],
                "address": port["device"],
                "kind": "serial",
                "source": "USB / Serial",
                "detail": port.get("manufacturer", ""),
            })
        self._set_discovery(results, "USB / Serial")

    def discover_ble(self):
        results = list_ble_devices()
        if not results:
            self.discovery_status.setText("No BLE results. Install optional BLE support with: pip install -e '.[ble]'")
        self._set_discovery(results, "Bluetooth LE")

    def add_discovered(self):
        rows = self.discovery_table.selectionModel().selectedRows()
        if not rows:
            return
        item = self.discovery_results[rows[0].row()]
        metadata = {}
        if item.get("mac"):
            metadata["mac"] = item["mac"]
        device = Device(
            id=str(uuid4()),
            name=item.get("name") or item.get("address") or "Discovered device",
            kind=item.get("kind", "network"),
            address=item.get("address", ""),
            port=item.get("port"),
            connection=item.get("protocol", "auto") or "auto",
            metadata=metadata,
            tags=["discovered"],
        )
        if device.connection == "auto" and device.port:
            if device.port == 22:
                device.connection = "ssh"
            elif device.port in (80, 443, 8080, 8443):
                device.connection = "http"
            elif device.port == 1883:
                device.connection = "mqtt"
        if device.address:
            result = run_connection_test(device)
            device.status = "online" if result.ok else "unknown"
            if result.ok:
                device.touch()
        self.storage.save_device(device)
        self.storage.add_event("info", "discovery", f"Added discovered device {device.name}")
        self.refresh()

    def remove_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        name = self.table.item(rows[0].row(), 0).text()
        devices = self.storage.list_devices()
        target = next((d for d in devices if d.name == name), None)
        if not target:
            return
        confirm = QMessageBox.question(self, "Remove device", f"Remove '{target.name}' from Fexus?")
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
            try:
                port = int(port_text)
            except ValueError:
                self.network_result.setText("TCP port must be a number.")
                return
            result = tcp_probe(host, port)
            self.network_result.setText(
                f"{host}:{port}\n"
                f"Reachable: {result.get('reachable')}\n"
                f"Latency: {result.get('latency_ms', '—')} ms\n"
                f"{result.get('error', '')}"
            )
        else:
            result = ping(host)
            self.network_result.setText(f"{host}\nReachable: {result['reachable']}")
