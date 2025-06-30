from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PySide6.QtSvgWidgets import QSvgWidget

from src.utils.resource_manager import ResourceManager


class LogoSection(QWidget):
    """Widget to display the logo in the sidebar."""

    def __init__(
        self,
        logo_path=ResourceManager.get_icon_path("Logo-CookiNUM-v.svg"),
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("logo_section")

        # audio player for recording sound
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)

        self._setup_ui()
        self._load_svg(logo_path)

    def _setup_ui(self):
        """Sets up the SVG widget and layout."""
        self.svg_widget = QSvgWidget()
        self.svg_widget.setObjectName("logo_svg")

        # Add recording indicator below the logo
        self.recording_indicator = QLabel("Enregistrement")
        self.recording_indicator.setObjectName("recording_indicator")
        self.recording_indicator.setVisible(False)
        self.recording_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a container widget for centering
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(
            self.svg_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        container_layout.addWidget(
            self.recording_indicator, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(container)

    def _load_svg(self, logo_path):
        """Loads the SVG file."""
        self.svg_widget.load(str(logo_path))
        if self.width() > 0:
            self.update_logo_size(self.width())
        else:
            self.update_logo_size(200)

    def update_logo_size(self, sidebar_width):
        """Resizes the SVG logo based on the available width."""
        # Sizing constraints
        scale_factor = 0.45
        available_width = max(1, sidebar_width)
        new_width = int(available_width * scale_factor)

        # Get the original size of the SVG
        renderer = self.svg_widget.renderer()
        if renderer.isValid():
            original_size = renderer.defaultSize()
            if original_size.width() > 0:
                # Calculate height maintaining aspect ratio
                aspect_ratio = original_size.height() / original_size.width()
                new_height = int(new_width * aspect_ratio)

                # Update the SVG widget size
                self.svg_widget.setFixedSize(new_width, new_height)
                self.svg_widget.updateGeometry()

    def on_recording_state_changed(self, is_recording: bool = False):
        """Show or hide the recording indicator overlay and play sound."""
        self.recording_indicator.setVisible(is_recording)

        # Play recording start sound
        sound_path = ResourceManager.get_sound_path("recording_sound.wav")
        self.audio_player.setSource(QUrl.fromLocalFile(str(sound_path)))
        self.audio_player.play()

    def resizeEvent(self, event):
        """Handle the section's own resize events."""
        super().resizeEvent(event)
        self.update_logo_size(self.width())
