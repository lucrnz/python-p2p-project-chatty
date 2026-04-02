from PySide6.QtCore import Qt

from chatty import create_window


def test_window_title(qtbot):
    window = create_window()
    qtbot.addWidget(window)
    assert window.windowTitle() == "Chatty"


def test_window_size(qtbot):
    window = create_window()
    qtbot.addWidget(window)
    assert window.width() == 400
    assert window.height() == 300


def test_label_text(qtbot):
    window = create_window()
    qtbot.addWidget(window)
    label = window.findChild(object)
    assert label is not None
    assert label.text() == "Hello from Chatty!"
