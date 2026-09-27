import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Device


class Storage:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          kind TEXT NOT NULL,
          address TEXT,
          port INTEGER,
          status TEXT NOT NULL,
          username TEXT,
          connection TEXT NOT NULL DEFAULT 'auto',
          tags TEXT NOT NULL,
          metadata TEXT NOT NULL,
          last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          level TEXT NOT NULL,
          source TEXT NOT NULL,
          message TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)
        self._ensure_column("devices", "connection", "TEXT NOT NULL DEFAULT 'auto'")
        self.conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        columns = {row[1] for row in self.conn.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def close(self):
        self.conn.close()

    def save_device(self, device: Device):
        self.conn.execute("""
        INSERT INTO devices (id,name,kind,address,port,status,username,connection,tags,metadata,last_seen)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name, kind=excluded.kind, address=excluded.address,
          port=excluded.port, status=excluded.status, username=excluded.username,
          connection=excluded.connection, tags=excluded.tags, metadata=excluded.metadata,
          last_seen=excluded.last_seen
        """, (
            device.id, device.name, device.kind, device.address, device.port,
            device.status, device.username, device.connection, json.dumps(device.tags),
            json.dumps(device.metadata), device.last_seen.isoformat() if device.last_seen else None,
        ))
        self.conn.commit()

    def list_devices(self) -> list[Device]:
        rows = self.conn.execute("SELECT * FROM devices ORDER BY name COLLATE NOCASE").fetchall()
        return [self._row(r) for r in rows]

    def delete_device(self, device_id: str):
        self.conn.execute("DELETE FROM devices WHERE id=?", (device_id,))
        self.conn.commit()

    def add_event(self, level: str, source: str, message: str):
        self.conn.execute(
            "INSERT INTO events(level,source,message,created_at) VALUES(?,?,?,?)",
            (level, source, message, datetime.now().astimezone().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def recent_events(self, limit=100):
        return self.conn.execute(
            "SELECT level,source,message,created_at FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    @staticmethod
    def _row(row) -> Device:
        return Device(
            id=row["id"],
            name=row["name"],
            kind=row["kind"],
            address=row["address"] or "",
            port=row["port"],
            status=row["status"],
            username=row["username"] or "",
            connection=row["connection"] or "auto",
            tags=json.loads(row["tags"] or "[]"),
            metadata=json.loads(row["metadata"] or "{}"),
            last_seen=datetime.fromisoformat(row["last_seen"]) if row["last_seen"] else None,
        )
