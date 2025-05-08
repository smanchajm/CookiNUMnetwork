from PyQt6.QtWidgets import QFrame, QLabel, QPushButton
from PyQt6.QtCore import Qt
import os

from src.ui.utils.layouts import create_vbox_layout
from src.core.video_processing.player import VLCPlayer


class MediaLiveSection(QFrame):
    """
    MediaPlayer section dedicated to live mode.
    Displays either RTMP stream or connection instructions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("media_live_section")
        self.is_rtmp_connected = False

        # Initialiser le lecteur VLC
        self.player = VLCPlayer()

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

        # Add test button
        self.test_button = QPushButton("Test Streaming", self.video_frame)
        self.test_button.setObjectName("test_button")
        self.test_button.clicked.connect(self.on_test_streaming)
        self.test_button.raise_()

        # Créer le layout
        main_layout = create_vbox_layout(
            widgets=[self.video_frame], spacing=0, margins=(0, 0, 0, 0)
        )
        self.setLayout(main_layout)

    def on_test_streaming(self):
        """Start streaming in test mode."""
        self.on_streaming_started()

    def on_streaming_started(self):
        """Handle streaming start."""
        self.is_rtmp_connected = True
        self._update_display()

        # Configurer le lecteur pour lire le flux RTMP
        self.player.load("rtmp://localhost:1935/live")
        self.player.set_video_output(self.video_frame.winId())
        self.player.play()

    def on_streaming_stopped(self):
        """Handle streaming stop."""
        self.is_rtmp_connected = False
        self._update_display()
        self.player.stop()

    def _update_display(self):
        """Update display based on connection state."""
        self.instructions_label.setVisible(not self.is_rtmp_connected)
        self.test_button.setVisible(not self.is_rtmp_connected)

    def set_recording_indicator(self, visible: bool):
        """Show or hide the recording indicator overlay."""
        self.recording_indicator.setVisible(visible)

    def resizeEvent(self, event):
        """Resize video widget when window is resized."""
        super().resizeEvent(event)
        if self.is_rtmp_connected and hasattr(self.video_frame, "winId"):
            self.player.set_video_output(self.video_frame.winId())
