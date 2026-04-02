from chatty import main


def test_main_is_callable():
    """The console-script entry-point must be importable and callable."""
    assert callable(main)
