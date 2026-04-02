import sys

from PySide6.QtWidgets import QApplication, QLabel, QWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Chatty")
    window.resize(400, 300)
    label = QLabel("Hello from Chatty!", window)
    window.show()
    sys.exit(app.exec())
