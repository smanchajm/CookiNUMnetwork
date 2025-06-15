from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
)

from src.ui.sections.sidebar_logo_section import LogoSection
from src.ui.sections.sidebar_actions_section import ActionButtonsSection
from src.ui.sections.sidebar_tags_section import TagListSection
from src.ui.utils.layouts import create_vbox_layout


class Sidebar(QFrame):
    """Main sidebar widget composed of separate sections."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")

        self._setup_ui()

    def _setup_ui(self):
        """Create section sections and arrange them in the layout."""
        self.logo_section = LogoSection()
        self.action_section = ActionButtonsSection()
        self.tag_section = TagListSection()

        self.tag_section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        main_layout = create_vbox_layout(
            widgets=[self.logo_section, self.action_section, self.tag_section],
            spacing=18,
            margins=(10, 5, 10, 10),
        )
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """Handle sidebar resizing, pass width to logo section."""
        super().resizeEvent(event)
        self.logo_section.update_logo_size(event.size().width())
