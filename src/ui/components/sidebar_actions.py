from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.core import constants
from src.core.event_handler import events
from src.core.video_processing.mode_service import Mode
from src.ui.utils.layouts import create_vbox_layout
from src.ui.widgets.action_button import ActionButton
from src.ui.widgets.separator import Separator
from src.utils.resource_manager import ResourceManager


class ActionButtonsSection(QWidget):
    """Widget containing the main action buttons (Open, Record, GoPro)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("action_section")

        self.mode_buttons_data = [
            (
                "Mode Direct",
                "live_mode_btn",
                ResourceManager.get_icon_path("camera_video.svg"),
                events.live_mode_clicked,
            ),
            (
                "Mode Replay",
                "review_mode_btn",
                ResourceManager.get_icon_path("movie.svg"),
                events.review_mode_clicked,
            ),
        ]

        self.action_buttons_data = [
            (
                "Ouvrir une vidéo",
                "open_video_btn",
                ResourceManager.get_icon_path("folder_open.svg"),
                events.open_video_clicked,
            ),
            (
                "Enregistrer",
                "start_recording_btn",
                ResourceManager.get_icon_path("radio_button_checked.svg"),
                events.start_recording_clicked,
            ),
            (
                "Connexion GoPro",
                "connect_gopro_btn",
                ResourceManager.get_icon_path("qr_code_scanner.svg"),
                events.connect_gopro_clicked,
            ),
            (
                "Connexion WiFi",
                "connect_wifi_btn",
                ResourceManager.get_icon_path("wifi.svg"),
                events.connect_wifi_clicked,
            ),
        ]

        # Définir les boutons par mode
        self.live_mode_buttons = [
            "start_recording_btn",
            "connect_gopro_btn",
            "connect_wifi_btn",
        ]
        self.review_mode_buttons = [
            "open_video_btn",
        ]

        self.buttons = {}
        self._setup_ui()

    def _setup_ui(self):
        """Creates the buttons and layout."""
        for text, name, icon_path, signal in self.mode_buttons_data:
            button = ActionButton(
                text=text, icon_path=icon_path, css_class="mode_button"
            )
            button.setObjectName(name)
            button.clicked.connect(signal.emit)
            self.buttons[name] = button

            # Initialiser la propriété active
            if name == "live_mode_btn":
                button.setProperty("active", "false")
            elif name == "review_mode_btn":
                button.setProperty("active", "true")

        self.buttons["separator_mode_section"] = Separator()

        for text, name, icon_path, signal in self.action_buttons_data:
            button = ActionButton(
                text=text, icon_path=icon_path, css_class="action_button"
            )
            button.setObjectName(name)
            button.clicked.connect(signal.emit)
            self.buttons[name] = button

        self.buttons["separator_tag_section"] = Separator()

        self.layout = create_vbox_layout(widgets=list(self.buttons.values()))
        self.setLayout(self.layout)

        # Calculer la largeur maximale
        max_width = max(button.sizeHint().width() for button in self.buttons.values())

        # Appliquer la hauteur maximale à tous les boutons
        for button in self.buttons.values():
            button.setFixedWidth(max_width)

    def update_recording_state(self, is_recording: bool) -> None:
        """
        Met à jour l'apparence du bouton d'enregistrement en fonction de l'état.
        """
        button = self.buttons["start_recording_btn"]
        if is_recording:
            button.setText("Stop")
        else:
            button.setText("Enregistrer")

    def on_live_mode_changed(self, is_live_mode: bool) -> None:
        """
        Gère les changements de visibilité des boutons en fonction du mode.
        """
        # Mettre à jour la visibilité des boutons
        for button in self.live_mode_buttons:
            self.buttons[button].setVisible(is_live_mode)
        for button in self.review_mode_buttons:
            self.buttons[button].setVisible(not is_live_mode)

        # Mettre à jour l'état actif des boutons de mode
        self.buttons["live_mode_btn"].setProperty(
            "active", "true" if is_live_mode else "false"
        )
        self.buttons["review_mode_btn"].setProperty(
            "active", "true" if not is_live_mode else "false"
        )

        # Forcer la mise à jour du style
        self.buttons["live_mode_btn"].style().unpolish(self.buttons["live_mode_btn"])
        self.buttons["live_mode_btn"].style().polish(self.buttons["live_mode_btn"])
        self.buttons["review_mode_btn"].style().unpolish(
            self.buttons["review_mode_btn"]
        )
        self.buttons["review_mode_btn"].style().polish(self.buttons["review_mode_btn"])
