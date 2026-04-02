"""Main window for Chatty – sidebar with room list + chat panel."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from chatty.models import Message, RoomInfo
from chatty.network import Discovery, RoomClient, RoomHost
from chatty.ui.styles import MAIN_STYLE


# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------


class UsernameDialog(QDialog):
    """Startup dialog that asks for a display name."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to Chatty")
        self.setFixedSize(360, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 28)

        title = QLabel("Choose your display name")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Username…")
        self.input.setMaxLength(24)
        layout.addWidget(self.input)

        self.ok_btn = QPushButton("Start Chatting")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)
        layout.addWidget(self.ok_btn)

        self.input.textChanged.connect(
            lambda t: self.ok_btn.setEnabled(bool(t.strip()))
        )
        self.input.returnPressed.connect(
            lambda: self.accept() if self.input.text().strip() else None
        )

    def username(self) -> str:
        return self.input.text().strip()


class CreateRoomDialog(QDialog):
    """Simple dialog to name a new room."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create Room")
        self.setFixedSize(360, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 28)

        title = QLabel("Room name")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g. General Chat")
        self.input.setMaxLength(30)
        layout.addWidget(self.input)

        self.ok_btn = QPushButton("Create")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)
        layout.addWidget(self.ok_btn)

        self.input.textChanged.connect(
            lambda t: self.ok_btn.setEnabled(bool(t.strip()))
        )
        self.input.returnPressed.connect(
            lambda: self.accept() if self.input.text().strip() else None
        )

    def room_name(self) -> str:
        return self.input.text().strip()


# ---------------------------------------------------------------------------
# Chat bubble widget
# ---------------------------------------------------------------------------


class MessageBubble(QFrame):
    """A single chat message rendered as a Telegram-style bubble."""

    def __init__(
        self, msg: Message, is_own: bool, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        if msg.is_system:
            self._build_system(msg)
        else:
            self._build_chat(msg, is_own)

    # -- system (centred, muted) -----------------------------------------------

    def _build_system(self, msg: Message) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 4, 20, 4)
        lbl = QLabel(msg.text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #4a5568; font-size: 12px; font-style: italic;")
        layout.addWidget(lbl)

    # -- regular chat bubble ---------------------------------------------------

    def _build_chat(self, msg: Message, is_own: bool) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 2, 12, 2)

        bubble = QFrame()
        bubble.setMaximumWidth(480)
        bl = QVBoxLayout(bubble)
        bl.setContentsMargins(12, 8, 12, 8)
        bl.setSpacing(4)

        if is_own:
            bubble.setStyleSheet(
                "QFrame { background-color: #2b5278; border-radius: 12px;"
                " border-top-right-radius: 4px; }"
            )
            outer.addStretch()
            outer.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                "QFrame { background-color: #182533; border-radius: 12px;"
                " border-top-left-radius: 4px; }"
            )
            name = QLabel(msg.username)
            name.setStyleSheet(
                "color: #5eaed5; font-size: 12px; font-weight: bold;"
            )
            bl.addWidget(name)
            outer.addWidget(bubble)
            outer.addStretch()

        text = QLabel(msg.text)
        text.setWordWrap(True)
        text.setStyleSheet("color: #f5f5f5; font-size: 14px;")
        text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        bl.addWidget(text)

        ts = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M")
        time_lbl = QLabel(ts)
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_lbl.setStyleSheet("color: #6d8396; font-size: 10px;")
        bl.addWidget(time_lbl)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class MainWindow(QMainWindow):
    """Top-level window: sidebar (rooms) + chat panel."""

    def __init__(
        self, username: str, *, start_discovery: bool = True
    ) -> None:
        super().__init__()
        self.setWindowTitle("Chatty")
        self.resize(900, 600)
        self.setMinimumSize(700, 400)

        self._username = username
        self._host: RoomHost | None = None
        self._client: RoomClient | None = None
        self._current_room: str | None = None
        self._rooms: dict[str, RoomInfo] = {}

        self._build_ui()
        self.setStyleSheet(MAIN_STYLE)

        # Network discovery
        self._discovery = Discovery(self)
        self._discovery.room_found.connect(self._on_room_found)
        self._discovery.room_removed.connect(self._on_room_removed)
        if start_discovery:
            self._discovery.start()

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_chat_panel(), 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        vbox = QVBoxLayout(sidebar)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        title = QLabel("  💬  Chatty")
        title.setObjectName("appTitle")
        vbox.addWidget(title)

        btn = QPushButton("＋  Create Room")
        btn.setObjectName("createRoomBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._on_create_room)
        vbox.addWidget(btn)

        self._room_list = QListWidget()
        self._room_list.setObjectName("roomList")
        self._room_list.itemClicked.connect(self._on_room_clicked)
        vbox.addWidget(self._room_list)

        return sidebar

    def _build_chat_panel(self) -> QWidget:
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # ── header ──
        self._chat_header = QWidget()
        self._chat_header.setObjectName("chatHeader")
        hdr = QVBoxLayout(self._chat_header)
        hdr.setContentsMargins(20, 12, 20, 12)
        hdr.setSpacing(2)
        self._room_title = QLabel()
        self._room_title.setObjectName("roomTitle")
        self._member_count = QLabel()
        self._member_count.setObjectName("memberCount")
        hdr.addWidget(self._room_title)
        hdr.addWidget(self._member_count)
        self._chat_header.hide()
        vbox.addWidget(self._chat_header)

        # ── message area ──
        self._scroll = QScrollArea()
        self._scroll.setObjectName("chatScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._msg_container = QWidget()
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setContentsMargins(0, 8, 0, 8)
        self._msg_layout.setSpacing(2)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_container)
        self._scroll.hide()

        # ── welcome label (no room selected) ──
        self._welcome = QLabel("Select or create a room to start chatting")
        self._welcome.setObjectName("welcomeLabel")
        self._welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(self._welcome, 1)
        vbox.addWidget(self._scroll, 1)

        # ── input bar ──
        self._input_area = QWidget()
        self._input_area.setObjectName("inputArea")
        ibox = QHBoxLayout(self._input_area)
        ibox.setContentsMargins(16, 12, 16, 12)
        ibox.setSpacing(8)

        self._msg_input = QLineEdit()
        self._msg_input.setObjectName("messageInput")
        self._msg_input.setPlaceholderText("Write a message…")
        self._msg_input.returnPressed.connect(self._on_send)
        ibox.addWidget(self._msg_input, 1)

        send = QPushButton("Send  ➤")
        send.setObjectName("sendBtn")
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.clicked.connect(self._on_send)
        ibox.addWidget(send)

        self._input_area.hide()
        vbox.addWidget(self._input_area)

        return panel

    # ── Room management ──────────────────────────────────────────────

    @Slot()
    def _on_create_room(self) -> None:
        dlg = CreateRoomDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.room_name()
        if not name:
            return
        self._leave_current_room()

        self._host = RoomHost(self._username, self)
        self._host.message_received.connect(self._on_message)
        self._host.member_joined.connect(self._on_member_change)
        self._host.member_left.connect(self._on_member_change)
        port = self._host.start()

        self._discovery.register_room(name, port)
        self._current_room = name

        # Ensure the room is visible in the sidebar immediately
        if name not in self._rooms:
            self._rooms[name] = RoomInfo(name=name, host="127.0.0.1", port=port)
            self._room_list.addItem(name)
        self._select_room_in_list(name)
        self._activate_chat(name)

    @Slot(QListWidgetItem)
    def _on_room_clicked(self, item: QListWidgetItem) -> None:
        name = item.text()
        if name == self._current_room:
            return
        room = self._rooms.get(name)
        if room is None:
            return
        self._leave_current_room()

        self._client = RoomClient(self._username, self)
        self._client.message_received.connect(self._on_message)
        self._client.disconnected.connect(self._on_disconnected)
        try:
            self._client.connect_to(room.host, room.port)
        except OSError:
            self._client = None
            return

        self._current_room = name
        self._activate_chat(name)

    def _leave_current_room(self) -> None:
        if self._host:
            self._discovery.unregister_room()
            self._host.stop()
            self._host = None
        if self._client:
            self._client.disconnect()
            self._client = None
        self._current_room = None

    def _activate_chat(self, name: str) -> None:
        self._room_title.setText(name)
        self._on_member_change()
        self._chat_header.show()
        self._welcome.hide()
        self._scroll.show()
        self._input_area.show()
        self._clear_messages()
        self._msg_input.setFocus()

    def _clear_messages(self) -> None:
        while self._msg_layout.count() > 1:  # keep trailing stretch
            item = self._msg_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _select_room_in_list(self, name: str) -> None:
        for i in range(self._room_list.count()):
            if self._room_list.item(i).text() == name:
                self._room_list.setCurrentRow(i)
                return

    # ── Messaging ────────────────────────────────────────────────────

    @Slot()
    def _on_send(self) -> None:
        text = self._msg_input.text().strip()
        if not text:
            return
        self._msg_input.clear()

        msg = Message(username=self._username, text=text)

        if self._host:
            self._host.broadcast(msg)
            self._add_bubble(msg, is_own=True)
        elif self._client:
            self._client.send_message(text)
            self._add_bubble(msg, is_own=True)

    @Slot(object)
    def _on_message(self, msg: Message) -> None:
        # Own non-system messages are already rendered optimistically
        if msg.username == self._username and not msg.is_system:
            return
        self._add_bubble(msg, is_own=False)

    def _add_bubble(self, msg: Message, *, is_own: bool) -> None:
        bubble = MessageBubble(msg, is_own)
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, bubble)
        QTimer.singleShot(30, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Discovery callbacks ──────────────────────────────────────────

    @Slot(object)
    def _on_room_found(self, room: RoomInfo) -> None:
        if room.name in self._rooms:
            return
        self._rooms[room.name] = room
        self._room_list.addItem(room.name)

    @Slot(str)
    def _on_room_removed(self, name: str) -> None:
        self._rooms.pop(name, None)
        for i in range(self._room_list.count()):
            if self._room_list.item(i).text() == name:
                self._room_list.takeItem(i)
                break
        if name == self._current_room:
            self._on_disconnected()

    @Slot()
    def _on_disconnected(self) -> None:
        self._leave_current_room()
        self._chat_header.hide()
        self._input_area.hide()
        self._scroll.hide()
        self._welcome.setText("Disconnected — select or create a room")
        self._welcome.show()

    @Slot()
    def _on_member_change(self, *_args: object) -> None:
        if self._host:
            n = len(self._host.members())
            self._member_count.setText(
                f"{n} member{'s' if n != 1 else ''} online"
            )
        elif self._client:
            self._member_count.setText("Connected")
        else:
            self._member_count.clear()

    # ── Lifecycle ────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        self._leave_current_room()
        self._discovery.stop()
        super().closeEvent(event)
