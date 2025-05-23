from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt


class ActionButton(QPushButton):
    """A reusable QPushButton specialized for main sidebar actions."""

    DEFAULT_ICON_SIZE = QSize(20, 20)

    def __init__(
        self,
        text: str = None,
        icon_path: str = None,
        css_class: str = None,
        icon_size: QSize = None,
        parent=None,
    ):
        super().__init__(text, parent)
        self._css_class = css_class
        self._icon_size = icon_size or self.DEFAULT_ICON_SIZE

        # Activer les propriétés nécessaires pour les états
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setMouseTracking(True)

        self._setup_icon(icon_path)
        self._setup_appearance()

    def _setup_icon(self, icon_path: str):
        """Loads and sets the button icon."""
        icon = QIcon(icon_path)
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(self._icon_size)

    def _setup_appearance(self):
        """Sets common appearance properties."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if self._css_class:
            self.setProperty("class", self._css_class)

    def set_icon_size(self, width, height):
        """Set custom icon size and return self for method chaining."""
        self._icon_size = QSize(width, height)
        self.setIconSize(self._icon_size)
        return self
