"""Common layout patterns for UI sections."""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QWidget,
    QLabel,
    QFrame,
    QLayout,
)
from PySide6.QtCore import Qt


def create_form_layout(
    field_pairs, spacing=10, label_alignment=Qt.AlignmentFlag.AlignRight
):
    """
    Create a form layout with label-widget pairs.

    Args:
        field_pairs: List of (label, widget) tuples, where label can be str or QWidget
        spacing: Spacing between rows
        label_alignment: Alignment for labels

    Returns:
        QFormLayout with the fields added
    """
    layout = QFormLayout()
    layout.setSpacing(spacing)
    layout.setLabelAlignment(label_alignment)

    for label, widget in field_pairs:
        if isinstance(label, str):
            label = QLabel(label)
        layout.addRow(label, widget)

    return layout


def create_vbox_layout(widgets, spacing=10, margins=(0, 0, 0, 0), alignment=None):
    """
    Create a vertical box layout with the given widgets or layouts.

    Args:
        widgets: List of widgets or layouts to add
        spacing: Spacing between widgets
        margins: Tuple of (left, top, right, bottom) margins
        alignment: Optional alignment for the widgets

    Returns:
        QVBoxLayout with the widgets/layouts added
    """
    layout = QVBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)

    for item in widgets:
        if isinstance(item, QLayout):
            layout.addLayout(item)
        elif alignment:
            layout.addWidget(item, alignment=alignment)
        else:
            layout.addWidget(item)

    return layout


def create_hbox_layout(widgets, spacing=10, margins=(0, 0, 0, 0), alignment=None):
    """
    Create a horizontal box layout with the given widgets or layouts.

    Args:
        widgets: List of widgets or layouts to add
        spacing: Spacing between widgets
        margins: Tuple of (left, top, right, bottom) margins
        alignment: Optional alignment for the widgets

    Returns:
        QHBoxLayout with the widgets/layouts added
    """
    layout = QHBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)

    for item in widgets:
        if isinstance(item, QLayout):
            layout.addLayout(item)
        elif alignment:
            layout.addWidget(item, alignment=alignment)
        else:
            layout.addWidget(item)

    return layout


def create_column_container(widgets, spacing=10, margins=(0, 0, 0, 0)):
    """
    Create a widget with a vertical layout containing the given widgets.

    Args:
        widgets: List of widgets to add
        spacing: Spacing between widgets
        margins: Tuple of (left, top, right, bottom) margins

    Returns:
        QWidget with a vertical layout containing the widgets
    """
    container = QWidget()
    layout = create_vbox_layout(widgets, spacing, margins)
    container.setLayout(layout)
    return container


def create_row_container(widgets, spacing=10, margins=(0, 0, 0, 0)):
    """
    Create a widget with a horizontal layout containing the given widgets.

    Args:
        widgets: List of widgets to add
        spacing: Spacing between widgets
        margins: Tuple of (left, top, right, bottom) margins

    Returns:
        QWidget with a horizontal layout containing the widgets
    """
    container = QWidget()
    layout = create_hbox_layout(widgets, spacing, margins)
    container.setLayout(layout)
    return container


def create_horizontal_separator():
    """Create a horizontal separator line."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


def create_vertical_separator():
    """Create a vertical separator line."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line
