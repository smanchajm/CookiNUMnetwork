import time

from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QFrame, QLabel

from src.core.logging_config import logger
from src.core.video_processing.player import VLCPlayer
from src.ui.utils.layouts import create_vbox_layout
from src.utils.resource_manager import ResourceManager


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
        self.player.media_player.options = [
            "--rtsp-udp",
            "--no-rtsp-tcp",
            "--network-caching=50",  # 50 ms de buffer réseau
            "--no-drop-late-frames",
            "--no-skip-frames",
        ]

        # audio player
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)

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

        # Créer le layout
        main_layout = create_vbox_layout(
            widgets=[self.video_frame], spacing=0, margins=(0, 0, 0, 0)
        )
        self.setLayout(main_layout)

    def on_streaming_started(self):
        """Handle streaming start."""
        time.sleep(3)  # buffer
        self.is_rtmp_connected = True
        self._update_display()

        logger.info("on_streaming_started")
        self.player.load(ResourceManager.get_gopro_rtsp_url())
        if self.video_frame.winId():
            self.player.set_video_output(self.video_frame.winId())
            self.player.play()

    def on_streaming_stopped(self):
        """Handle streaming stop."""
        self.is_rtmp_connected = False
        self._update_display()
        self.player.stop()
        # Reset player state
        self.player.media_player.release()
        self.player = VLCPlayer()

    def on_streaming_error(self, error: str):
        """Handle streaming error."""
        logger.error(f"Streaming error in MediaLiveSection: {error}")
        self.on_streaming_stopped()  # Use same cleanup as stop

    def _update_display(self):
        """Update display based on connection state."""
        self.instructions_label.setVisible(not self.is_rtmp_connected)

    def on_recording_state_changed(self, is_recording: bool = False):
        """Show or hide the recording indicator overlay and play sound."""
        self.recording_indicator.setVisible(is_recording)
        self.recording_indicator.raise_()

        # Play recording start sound
        sound_path = ResourceManager.get_sound_path("recording_sound.wav")
        self.audio_player.setSource(QUrl.fromLocalFile(str(sound_path)))
        self.audio_player.play()

    def resizeEvent(self, event):
        """Resize video widget when window is resized."""
        super().resizeEvent(event)
        if self.is_rtmp_connected and hasattr(self.video_frame, "winId"):
            self.player.set_video_output(self.video_frame.winId())
