"""QSS stylesheets for the Chatty UI – dark Telegram-inspired palette."""

MAIN_STYLE = """
/* ── Base ──────────────────────────────────────────────────────────── */
QWidget {
    background-color: #0e1621;
    color: #f5f5f5;
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, sans-serif;
    font-size: 14px;
}

/* ── Sidebar ───────────────────────────────────────────────────────── */
#sidebar {
    background-color: #17212b;
    border-right: 1px solid #232e3c;
}

#appTitle {
    font-size: 20px;
    font-weight: bold;
    color: #f5f5f5;
    padding: 16px 16px 8px 16px;
}

#roomList {
    background-color: transparent;
    border: none;
    outline: none;
}
#roomList::item {
    padding: 14px 16px;
    border-bottom: 1px solid #232e3c;
    color: #f5f5f5;
    font-size: 14px;
}
#roomList::item:selected {
    background-color: #2b5278;
}
#roomList::item:hover {
    background-color: #1e2c3a;
}

QPushButton#createRoomBtn {
    background-color: #2b5278;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: bold;
    margin: 8px 12px;
}
QPushButton#createRoomBtn:hover {
    background-color: #3a6a98;
}
QPushButton#createRoomBtn:pressed {
    background-color: #1e3f5c;
}

/* ── Chat header ───────────────────────────────────────────────────── */
#chatHeader {
    background-color: #17212b;
    border-bottom: 1px solid #232e3c;
}
#roomTitle {
    font-size: 16px;
    font-weight: bold;
    color: #f5f5f5;
}
#memberCount {
    font-size: 12px;
    color: #6d8396;
}

/* ── Chat scroll area ──────────────────────────────────────────────── */
#chatScroll {
    background-color: #0e1621;
    border: none;
}

/* ── Message input area ────────────────────────────────────────────── */
#inputArea {
    background-color: #17212b;
    border-top: 1px solid #232e3c;
}
#messageInput {
    background-color: #242f3d;
    color: #f5f5f5;
    border: none;
    border-radius: 20px;
    padding: 10px 16px;
    font-size: 14px;
    selection-background-color: #2b5278;
}
#messageInput:focus {
    background-color: #2b3845;
}

QPushButton#sendBtn {
    background-color: #5eaed5;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    min-width: 60px;
}
QPushButton#sendBtn:hover {
    background-color: #79c2e3;
}
QPushButton#sendBtn:pressed {
    background-color: #4a97be;
}
QPushButton#sendBtn:disabled {
    background-color: #2b3845;
    color: #4a5568;
}

/* ── Welcome / empty state ─────────────────────────────────────────── */
#welcomeLabel {
    font-size: 18px;
    color: #4a5568;
}

/* ── Scrollbars ────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2b3845;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #3a4a5a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* ── Dialogs ───────────────────────────────────────────────────────── */
QDialog {
    background-color: #17212b;
}
QDialog QLabel {
    color: #f5f5f5;
    font-size: 14px;
}
QDialog QLineEdit {
    background-color: #242f3d;
    color: #f5f5f5;
    border: 1px solid #2b5278;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    selection-background-color: #2b5278;
}
QDialog QPushButton {
    background-color: #2b5278;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}
QDialog QPushButton:hover {
    background-color: #3a6a98;
}
QDialog QPushButton:disabled {
    background-color: #1e2c3a;
    color: #4a5568;
}
"""
