"""UI widget tests for Chatty (no network access required)."""

from chatty.models import Message
from chatty.ui.main_window import (
    CreateRoomDialog,
    MainWindow,
    MessageBubble,
    UsernameDialog,
)


# -- MainWindow ---------------------------------------------------------------


def test_window_title(qtbot):
    w = MainWindow("Tester", start_discovery=False)
    qtbot.addWidget(w)
    assert w.windowTitle() == "Chatty"


def test_window_default_size(qtbot):
    w = MainWindow("Tester", start_discovery=False)
    qtbot.addWidget(w)
    assert w.width() == 900
    assert w.height() == 600


def test_sidebar_exists(qtbot):
    w = MainWindow("Tester", start_discovery=False)
    qtbot.addWidget(w)
    sidebar = w.centralWidget().findChild(type(w.centralWidget()), "sidebar")
    # sidebar is found by object name via the room list
    assert w._room_list is not None


# -- MessageBubble ------------------------------------------------------------


def test_own_message_bubble(qtbot):
    msg = Message(username="Me", text="Hello world!")
    bubble = MessageBubble(msg, is_own=True)
    qtbot.addWidget(bubble)
    assert bubble is not None


def test_other_message_bubble(qtbot):
    msg = Message(username="Alice", text="Hey there!")
    bubble = MessageBubble(msg, is_own=False)
    qtbot.addWidget(bubble)
    assert bubble is not None


def test_system_message_bubble(qtbot):
    msg = Message(username="", text="Alice joined the room", is_system=True)
    bubble = MessageBubble(msg, is_own=False)
    qtbot.addWidget(bubble)
    assert bubble is not None


# -- Dialogs ------------------------------------------------------------------


def test_username_dialog_starts_disabled(qtbot):
    dlg = UsernameDialog()
    qtbot.addWidget(dlg)
    assert not dlg.ok_btn.isEnabled()


def test_username_dialog_enables_on_text(qtbot):
    dlg = UsernameDialog()
    qtbot.addWidget(dlg)
    dlg.input.setText("Alice")
    assert dlg.ok_btn.isEnabled()
    assert dlg.username() == "Alice"


def test_create_room_dialog_starts_disabled(qtbot):
    dlg = CreateRoomDialog()
    qtbot.addWidget(dlg)
    assert not dlg.ok_btn.isEnabled()


def test_create_room_dialog_enables_on_text(qtbot):
    dlg = CreateRoomDialog()
    qtbot.addWidget(dlg)
    dlg.input.setText("General")
    assert dlg.ok_btn.isEnabled()
    assert dlg.room_name() == "General"
