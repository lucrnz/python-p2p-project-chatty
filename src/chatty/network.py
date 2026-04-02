"""Peer-to-peer networking for Chatty.

Room discovery uses Zeroconf (mDNS / DNS-SD).
Messaging uses TCP with newline-delimited JSON.
"""

from __future__ import annotations

import json
import logging
import socket
import threading
import time

from PySide6.QtCore import QObject, Signal
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

from chatty.models import Message, RoomInfo

logger = logging.getLogger(__name__)

SERVICE_TYPE = "_chatty._tcp.local."


def get_local_ip() -> str:
    """Return the primary local IP address of this machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


# ---------------------------------------------------------------------------
# Zeroconf room discovery
# ---------------------------------------------------------------------------


class Discovery(QObject):
    """Discovers and advertises Chatty rooms on the local network.

    Implements the ``zeroconf.ServiceListener`` protocol so it can be
    passed directly as a *listener* to :class:`ServiceBrowser`.
    """

    room_found = Signal(object)  # RoomInfo
    room_removed = Signal(str)  # room name

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._zc: Zeroconf | None = None
        self._browser: ServiceBrowser | None = None
        self._registered: ServiceInfo | None = None

    # -- public API -----------------------------------------------------------

    def start(self) -> None:
        """Begin browsing for ``_chatty._tcp`` services."""
        self._zc = Zeroconf()
        self._browser = ServiceBrowser(self._zc, SERVICE_TYPE, listener=self)

    def register_room(self, name: str, port: int) -> None:
        """Advertise a room called *name* at *port* on the LAN."""
        if self._zc is None:
            return
        ip = get_local_ip()
        self._registered = ServiceInfo(
            SERVICE_TYPE,
            f"{name}.{SERVICE_TYPE}",
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={b"room": name.encode()},
            server=f"{socket.gethostname()}.local.",
        )
        self._zc.register_service(self._registered)

    def unregister_room(self) -> None:
        """Remove a previously advertised room."""
        if self._registered and self._zc:
            self._zc.unregister_service(self._registered)
            self._registered = None

    def stop(self) -> None:
        """Tear down all discovery resources."""
        self.unregister_room()
        if self._browser:
            self._browser.cancel()
        if self._zc:
            self._zc.close()

    # -- zeroconf.ServiceListener callbacks (called from Zeroconf threads) ----

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info is None:
            return
        addrs = info.parsed_addresses()
        if not addrs:
            return
        room_name = info.properties.get(b"room", b"").decode() or name
        self.room_found.emit(RoomInfo(name=room_name, host=addrs[0], port=info.port))

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        room_name = name.replace(f".{SERVICE_TYPE}", "")
        self.room_removed.emit(room_name)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:  # noqa: D401
        """Not used – required by the listener protocol."""


# ---------------------------------------------------------------------------
# Room host (TCP server – star topology hub)
# ---------------------------------------------------------------------------


class RoomHost(QObject):
    """Hosts a chat room by running a TCP server.

    The host relays every incoming message to all other connected clients.
    """

    message_received = Signal(object)  # Message
    member_joined = Signal(str)
    member_left = Signal(str)

    def __init__(self, username: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._username = username
        self._sock: socket.socket | None = None
        self._clients: dict[str, socket.socket] = {}
        self._running = False
        self._lock = threading.Lock()

    @property
    def username(self) -> str:
        return self._username

    def start(self) -> int:
        """Bind and listen on a random free port.  Returns the port number."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("0.0.0.0", 0))
        self._sock.listen(16)
        self._running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        return self._sock.getsockname()[1]

    def broadcast(self, msg: Message, *, exclude: str | None = None) -> None:
        """Send *msg* to every connected client, optionally skipping *exclude*."""
        payload = _encode_message(msg)
        with self._lock:
            dead: list[str] = []
            for uname, sock in self._clients.items():
                if uname == exclude:
                    continue
                try:
                    sock.sendall(payload)
                except OSError:
                    dead.append(uname)
            for u in dead:
                self._drop(u)

    def members(self) -> list[str]:
        """Return a list of all participants including the host."""
        with self._lock:
            return [self._username, *self._clients]

    def stop(self) -> None:
        """Shut the server down and close every client socket."""
        self._running = False
        if self._sock:
            self._sock.close()
        with self._lock:
            for s in self._clients.values():
                try:
                    s.close()
                except OSError:
                    pass
            self._clients.clear()

    # -- internals ------------------------------------------------------------

    def _accept_loop(self) -> None:
        while self._running:
            try:
                if self._sock:
                    self._sock.settimeout(1.0)
                conn, _ = self._sock.accept()
                threading.Thread(
                    target=self._handle_client, args=(conn,), daemon=True
                ).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_client(self, conn: socket.socket) -> None:
        buf = ""
        uname: str | None = None
        try:
            while self._running:
                conn.settimeout(2.0)
                try:
                    chunk = conn.recv(4096)
                except socket.timeout:
                    continue
                if not chunk:
                    break
                buf += chunk.decode()
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    pkt = json.loads(line)
                    if pkt["type"] == "join":
                        uname = pkt["username"]
                        with self._lock:
                            self._clients[uname] = conn
                        self.member_joined.emit(uname)
                        sys_msg = Message(
                            username="",
                            text=f"{uname} joined the room",
                            is_system=True,
                        )
                        self.message_received.emit(sys_msg)
                        self.broadcast(sys_msg)
                    elif pkt["type"] == "message":
                        m = Message(
                            username=pkt["username"],
                            text=pkt["text"],
                            timestamp=pkt.get("timestamp", time.time()),
                        )
                        self.message_received.emit(m)
                        self.broadcast(m, exclude=uname)
        except Exception:
            logger.debug("client handler error", exc_info=True)
        finally:
            conn.close()
            if uname:
                self._drop(uname)
                sys_msg = Message(
                    username="",
                    text=f"{uname} left the room",
                    is_system=True,
                )
                self.message_received.emit(sys_msg)
                self.broadcast(sys_msg)
                self.member_left.emit(uname)

    def _drop(self, uname: str) -> None:
        with self._lock:
            s = self._clients.pop(uname, None)
        if s:
            try:
                s.close()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Room client (TCP client)
# ---------------------------------------------------------------------------


class RoomClient(QObject):
    """Connects to a :class:`RoomHost` and exchanges messages."""

    message_received = Signal(object)  # Message
    disconnected = Signal()

    def __init__(self, username: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._username = username
        self._sock: socket.socket | None = None
        self._running = False

    def connect_to(self, host: str, port: int) -> None:
        """Open a TCP connection and send the initial *join* handshake."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._running = True
        self._send({"type": "join", "username": self._username})
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def send_message(self, text: str) -> None:
        """Send a chat message to the room host."""
        self._send(
            {
                "type": "message",
                "username": self._username,
                "text": text,
                "timestamp": time.time(),
            }
        )

    def disconnect(self) -> None:
        """Close the connection."""
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass

    # -- internals ------------------------------------------------------------

    def _send(self, obj: dict) -> None:
        if self._sock:
            try:
                self._sock.sendall((json.dumps(obj) + "\n").encode())
            except OSError:
                self.disconnected.emit()

    def _recv_loop(self) -> None:
        buf = ""
        try:
            while self._running:
                if self._sock is None:
                    break
                self._sock.settimeout(2.0)
                try:
                    chunk = self._sock.recv(4096)
                except socket.timeout:
                    continue
                if not chunk:
                    break
                buf += chunk.decode()
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    pkt = json.loads(line)
                    if pkt["type"] == "message":
                        m = Message(
                            username=pkt["username"],
                            text=pkt["text"],
                            timestamp=pkt.get("timestamp", time.time()),
                            is_system=pkt.get("is_system", False),
                        )
                        self.message_received.emit(m)
        except Exception:
            logger.debug("recv loop error", exc_info=True)
        finally:
            self.disconnected.emit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _encode_message(msg: Message) -> bytes:
    """Serialise a :class:`Message` to newline-delimited JSON bytes."""
    return (
        json.dumps(
            {
                "type": "message",
                "username": msg.username,
                "text": msg.text,
                "timestamp": msg.timestamp,
                "is_system": msg.is_system,
            }
        )
        + "\n"
    ).encode()
