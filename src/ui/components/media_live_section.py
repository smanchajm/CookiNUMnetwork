from PyQt6.QtWidgets import QFrame, QLabel
from PyQt6.QtCore import Qt

from src.ui.utils.layouts import create_vbox_layout


class MediaLiveSection(QFrame):
    """
    Section du MediaPlayer dédiée au mode live.
    Affiche soit le flux RTMP, soit les instructions de connexion.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("media_live_section")
        self.is_rtmp_connected = False

        self.setup_ui()

    def setup_ui(self):
        self.video_frame = QFrame()
        self.video_frame.setObjectName("video_frame")

        # Add recording indicator overlay
        self.recording_indicator = QLabel("Enregistrement", self.video_frame)
        self.recording_indicator.setObjectName("recording_indicator")
        self.recording_indicator.setVisible(False)
        self.recording_indicator.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.recording_indicator.raise_()

        # Add instructions label for RTMP connection
        self.instructions_label = QLabel(self.video_frame)
        self.instructions_label.setObjectName("instructions_label")
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setText(
            "Pour afficher le flux RTMP :\n"
            "1. Renseignez le wifi\n"
            "2. Connectez-vous à la GoPro via WiFi\n"
        )
        self.instructions_label.raise_()

        # Créer le layout
        main_layout = create_vbox_layout(
            widgets=[self.video_frame], spacing=0, margins=(0, 0, 0, 0)
        )
        self.setLayout(main_layout)

    def set_rtmp_connected(self, is_connected):
        """Update RTMP connection state."""
        self.is_rtmp_connected = is_connected
        self._update_display()

    def _update_display(self):
        """Update the display based on connection state."""
        pass
        # if self.is_rtmp_connected:
        #     self.instructions_label.hide()
        #     self.video_frame.show()
        # else:
        #     self.instructions_label.show()
        #     self.video_frame.hide()

    def set_recording_indicator(self, visible: bool):
        """Show or hide the recording indicator overlay."""
        self.recording_indicator.setVisible(visible)
