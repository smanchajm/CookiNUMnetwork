from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from src.core.video_processing.tag_service import TagService
from src.ui.widgets.action_button import ActionButton
from src.ui.utils.layouts import create_vbox_layout
from src.ui.utils.qt_helpers import clear_layout
from src.core.event_handler import events


class TagListSection(QWidget):
    """Widget managing the tag list display and interaction."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tag_section")

        # Initialiser le gestionnaire de tags
        self.tag_manager = TagService()

        self._setup_ui()

    def on_tags_changed(self, new_tags_data):
        """Handle tags data changes."""
        self.tag_manager.tags = new_tags_data
        self.update_tag_display()

    def _setup_ui(self):
        """Sets up the title, button, scroll area, and layout."""
        # Créer les widgets principaux
        self.tag_list_title = QLabel("Tags")
        self.tag_list_title.setObjectName("tag_list_title")

        self.add_tag_button = ActionButton(
            text="Ajouter un tag", icon_path="src/ui/assets/icons/add.svg"
        )
        self.add_tag_button.setObjectName("add_tag_button")
        self.add_tag_button.clicked.connect(events.add_tag_clicked.emit)

        # Créer la zone de défilement
        self.tag_scroll_area = QScrollArea()
        self.tag_scroll_area.setObjectName("tag_scroll_area")
        self.tag_scroll_area.setWidgetResizable(True)
        self.tag_scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Créer le widget de contenu pour la zone de défilement
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_widget")

        # Utiliser la fonction helper pour créer le layout des tags
        self.tags_layout = create_vbox_layout(
            widgets=[], spacing=0, margins=(5, 5, 5, 5)
        )
        self.tags_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_widget.setLayout(self.tags_layout)
        self.tag_scroll_area.setWidget(self.scroll_widget)

        main_layout = create_vbox_layout(
            widgets=[self.tag_list_title, self.add_tag_button, self.tag_scroll_area],
            spacing=0,
            margins=(0, 0, 0, 0),
        )
        main_layout.setStretchFactor(self.tag_scroll_area, 1)

        self.setLayout(main_layout)
        self.update_tag_display()

    def update_tag_display(self):
        """Clears and repopulates the tag list display."""
        # Utiliser la fonction helper pour vider le layout
        clear_layout(self.tags_layout)

        # Add new tag widgets
        tags = self.tag_manager.get_tags()
        if not tags:
            tag_label = QLabel("Aucun tag")
            tag_label.setObjectName("tag_item_label")
            self.tags_layout.addWidget(tag_label)
        else:
            for timestamp, name, display_time in tags:  # Déballage du tuple
                tag_label = QLabel(f"{display_time}  {name}")
                tag_label.setObjectName("tag_item_label")

                # Rendre les tags cliquables
                tag_label.setCursor(Qt.CursorShape.PointingHandCursor)
                tag_label.mousePressEvent = (
                    lambda event, ts=timestamp: self._on_tag_item_clicked(ts)
                )
                self.tags_layout.addWidget(tag_label)

        # Add stretch at the end
        self.tags_layout.addStretch(1)

    def _on_tag_item_clicked(self, timestamp):
        """Handle tag item click event."""
        events.tag_selected.emit(timestamp)

    def set_tags(self, new_tags_data: list[tuple[str, str]]):
        """Updates the tags data and refreshes the display."""
        events.tags_changed.emit(new_tags_data)
