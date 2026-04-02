"""Tests for the network helpers (no LAN access needed)."""

from chatty.models import Message
from chatty.network import _encode_message, get_local_ip


def test_get_local_ip_returns_dotted_quad():
    ip = get_local_ip()
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(p.isdigit() for p in parts)


def test_encode_message_is_newline_terminated():
    msg = Message(username="A", text="hi", timestamp=1.0)
    raw = _encode_message(msg)
    assert raw.endswith(b"\n")


def test_encode_message_roundtrip():
    import json

    msg = Message(username="Bob", text="hello", timestamp=100.0, is_system=False)
    decoded = json.loads(_encode_message(msg).decode())
    assert decoded["type"] == "message"
    assert decoded["username"] == "Bob"
    assert decoded["text"] == "hello"
    assert decoded["timestamp"] == 100.0
    assert decoded["is_system"] is False
