"""Utility functions to simplify common Qt operations."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy, QSpacerItem


def set_margins(content, left=0, top=0, right=0, bottom=0):
    """Set the contents margins of a widget."""
    content.setContentsMargins(left, top, right, bottom)


def center_widget(widget, parent=None):
    """Center a widget on screen or within a parent widget."""
    if parent:
        geo = parent.geometry()
        x = (geo.width() - widget.width()) // 2
        y = (geo.height() - widget.height()) // 2
        widget.move(parent.x() + x, parent.y() + y)
    else:
        widget.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        widget.move(
            widget.screen().availableGeometry().center() - widget.rect().center()
        )


def create_spacer(width=0, height=0, h_policy=None, v_policy=None):
    """Create a spacer item with the specified size and policies."""
    if h_policy is None:
        h_policy = (
            QSizePolicy.Policy.Expanding if width == 0 else QSizePolicy.Policy.Fixed
        )
    if v_policy is None:
        v_policy = (
            QSizePolicy.Policy.Expanding if height == 0 else QSizePolicy.Policy.Fixed
        )

    return QSpacerItem(width, height, h_policy, v_policy)


def clear_layout(layout):
    """Remove all widgets from a layout."""
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
