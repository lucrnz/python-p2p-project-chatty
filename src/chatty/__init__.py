"""Chatty – peer-to-peer chat on your local network."""

import sys

from PySide6.QtWidgets import QApplication, QDialog

from chatty.ui.main_window import MainWindow, UsernameDialog


def main() -> None:
    """Application entry-point (called by the ``chatty`` console script)."""
    app = QApplication(sys.argv)

    dlg = UsernameDialog()
    if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.username():
        sys.exit(0)

    window = MainWindow(dlg.username())
    window.show()
    sys.exit(app.exec())
