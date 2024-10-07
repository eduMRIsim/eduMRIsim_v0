from contextlib import contextmanager


@contextmanager
def block_signals(widgets):
    """
    Context manager to temporarily block signal emissions for a group of widgets.
    :param widgets: List of widgets for which signal emissions should be blocked.
    """
    try:
        # Temporarily block signal emissions for each widget
        for widget in widgets:
            widget.blockSignals(True)
        # Yield control back to the caller
        yield
    finally:
        # Re-enable signal emissions for each widget, even if an exception occurred
        for widget in widgets:
            widget.blockSignals(False)
