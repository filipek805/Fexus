from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Device:
    id: str
    name: str
    kind: str
    address: str = ""
    port: int | None = None
    status: str = "unknown"
    username: str = ""
    connection: str = "auto"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    last_seen: datetime | None = None

    def touch(self) -> None:
        self.last_seen = datetime.now(timezone.utc)
