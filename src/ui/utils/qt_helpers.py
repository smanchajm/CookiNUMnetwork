"""Utility functions to simplify common Qt operations."""


def clear_layout(layout):
    """Remove all widgets from a layout."""
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
