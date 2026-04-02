"""Data models for Chatty."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Message:
    """A single chat message."""

    username: str
    text: str
    timestamp: float = field(default_factory=time.time)
    is_system: bool = False


@dataclass
class RoomInfo:
    """Metadata about a discovered room on the local network."""

    name: str
    host: str
    port: int
