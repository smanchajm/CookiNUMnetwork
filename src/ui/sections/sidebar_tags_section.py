from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

from src.core.event_handler import events
from src.ui.utils.layouts import create_vbox_layout
from src.ui.utils.qt_helpers import clear_layout
from src.ui.widgets.action_button import ActionButton
from src.utils.resource_manager import ResourceManager


class TagListSection(QWidget):
    """Widget managing the tag list display and interaction."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tag_section")
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the title, button, scroll area, and layout."""
        # Créer les widgets principaux
        self.tag_list_title = QLabel("Tags")
        self.tag_list_title.setObjectName("tag_list_title")

        self.add_tag_button = ActionButton(
            text="Ajouter un tag", icon_path=ResourceManager.get_icon_path("add.svg")
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

        self.setLayout(main_layout)

    def update_tag_display(self, tags: list[tuple[str, str, str]]):
        """Clears and repopulates the tag list display."""
        # Utiliser la fonction helper pour vider le layout
        clear_layout(self.tags_layout)
        if not tags:
            tag_label = QLabel("Aucun tag")
            tag_label.setObjectName("tag_item_label")
            self.tags_layout.addWidget(tag_label)
        else:
            # Calculer la largeur maximale nécessaire
            max_width = 0
            tag_labels = []

            # Première passe : créer tous les labels et trouver la largeur maximale
            for timestamp, name, display_time in tags:
                tag_label = QLabel(f"{display_time}  {name}")
                tag_label.setObjectName("tag_item_label")
                tag_label.setCursor(Qt.CursorShape.PointingHandCursor)
                tag_label.mousePressEvent = (
                    lambda event, ts=timestamp: self._on_tag_item_clicked(ts)
                )
                tag_labels.append((tag_label, timestamp))
                max_width = max(max_width, tag_label.sizeHint().width())

            # Deuxième passe : appliquer la largeur maximale et ajouter les widgets
            for tag_label, timestamp in tag_labels:
                tag_label.setFixedWidth(max_width)

                # Créer un widget horizontal pour contenir le label et le bouton
                tag_widget = QWidget()
                tag_layout = QHBoxLayout(tag_widget)
                tag_layout.setContentsMargins(0, 0, 0, 0)
                tag_layout.setSpacing(5)

                # Créer le bouton de suppression
                delete_button = ActionButton(
                    icon_path=ResourceManager.get_icon_path("delete.svg")
                )
                delete_button.setObjectName("delete_tag_button")
                delete_button.clicked.connect(
                    lambda checked, ts=timestamp: self._on_delete_tag_clicked(ts)
                )

                # Ajouter les widgets au layout horizontal
                tag_layout.addWidget(tag_label)
                tag_layout.addWidget(delete_button)
                tag_layout.addStretch()

                # Ajouter le widget horizontal au layout principal
                self.tags_layout.addWidget(tag_widget)

        # Add stretch at the end
        self.tags_layout.addStretch(1)

    def _on_tag_item_clicked(self, timestamp):
        """Handle tag item click event."""
        events.tag_selected.emit(timestamp)

    def _on_delete_tag_clicked(self, timestamp):
        """Handle delete tag button click event."""
        events.delete_tag.emit(timestamp)

    def set_tags(self, new_tags_data: list[tuple[str, str]]):
        """Updates the tags data and refreshes the display."""
        events.tags_changed.emit(new_tags_data)
