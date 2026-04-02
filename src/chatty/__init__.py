import sys

from PySide6.QtWidgets import QApplication, QLabel, QWidget


def create_window():
    window = QWidget()
    window.setWindowTitle("Chatty")
    window.resize(400, 300)
    label = QLabel("Hello from Chatty!", window)
    return window


def main():
    app = QApplication(sys.argv)
    window = create_window()
    window.show()
    sys.exit(app.exec())
