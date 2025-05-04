from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt


class ActionButton(QPushButton):
    """A reusable QPushButton specialized for main sidebar actions."""

    DEFAULT_ICON_SIZE = QSize(20, 20)

    def __init__(self, text: str = None, icon_path: str = None, parent=None):
        super().__init__(text, parent)

        self._setup_icon(icon_path)
        self._setup_appearance()

    def _setup_icon(self, icon_path: str):
        """Loads and sets the button icon."""
        icon = QIcon(icon_path)
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(self.DEFAULT_ICON_SIZE)

    def _setup_appearance(self):
        """Sets common appearance properties."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_icon_size(self, width, height):
        """Set custom icon size and return self for method chaining."""
        self.setIconSize(QSize(width, height))
        return self
