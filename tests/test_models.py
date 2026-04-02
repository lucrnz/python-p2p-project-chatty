"""Tests for data models."""

from chatty.models import Message, RoomInfo


def test_message_defaults():
    msg = Message(username="Alice", text="Hello")
    assert msg.username == "Alice"
    assert msg.text == "Hello"
    assert msg.is_system is False
    assert isinstance(msg.timestamp, float)
    assert msg.timestamp > 0


def test_message_system():
    msg = Message(username="", text="Bob joined", is_system=True)
    assert msg.is_system is True


def test_room_info():
    room = RoomInfo(name="General", host="192.168.1.10", port=9999)
    assert room.name == "General"
    assert room.host == "192.168.1.10"
    assert room.port == 9999
