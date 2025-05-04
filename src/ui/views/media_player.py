from PyQt6.QtWidgets import QFrame, QLabel
from PyQt6.QtCore import Qt

from src.core.video_processing.media_service import MediaService
from src.ui.components.media_controls import MediaControls
from src.ui.utils.layouts import create_vbox_layout


class MediaPlayer(QFrame):
    """
    Widget lecteur média avec contrôles personnalisés.
    """

    def __init__(self, media_service: MediaService, parent=None):
        super().__init__(parent)
        self.setObjectName("media_player")
        self.is_live_mode = False
        self.media_service = media_service

        self.setup_ui()

    def setup_ui(self):
        self.video_frame = QFrame()
        self.video_frame.setObjectName("video_frame")
        self.controls = MediaControls()

        # Add recording indicator overlay
        self.recording_indicator = QLabel("Enregistrement", self.video_frame)
        self.recording_indicator.setObjectName("recording_indicator")
        self.recording_indicator.setVisible(False)
        self.recording_indicator.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.recording_indicator.raise_()
        # Créer le layout en utilisant la fonction helper
        main_layout = create_vbox_layout(
            widgets=[self.video_frame, self.controls], spacing=0, margins=(0, 0, 0, 0)
        )

        # Donner plus d'espace au frame vidéo
        main_layout.setStretchFactor(self.video_frame, 1)

        self.setLayout(main_layout)

        if self.video_frame.winId():  # Assurer que winId est valide
            self.media_service.set_video_output(self.video_frame.winId())

    def on_play_state_changed(self, is_playing):
        """
        Met à jour l'interface en fonction de l'état de lecture.
        """
        if is_playing:
            self.controls.play_pause_btn._setup_icon("src/ui/assets/icons/pause.svg")
        else:
            self.controls.play_pause_btn._setup_icon(
                "src/ui/assets/icons/play_arrow.svg"
            )
        self.controls.is_playing = is_playing

    def on_position_changed(self, current_time, total_time):
        """
        Met à jour l'affichage de la timeline avec les temps actuels.
        """
        self.controls.update_timeline(current_time, total_time)

        # Mise à jour de la position du slider
        if total_time > 0:
            position_percent = (current_time / total_time) * 100
            self.controls.update_slider_position(position_percent)

    def on_live_mode_changed(self, is_live_mode):
        """Handle live mode state changes."""
        self.is_live_mode = is_live_mode
        if is_live_mode:
            self.controls.hide()
        else:
            self.controls.show()

    def add_tag_icon(self, timestamp, total_time):
        self.controls.on_add_tag(timestamp, total_time)

    def set_recording_indicator(self, visible: bool):
        """Show or hide the recording indicator overlay."""
        self.recording_indicator.setVisible(visible)

    def update_recording_state(self, is_recording: bool):
        """Affiche ou masque l'indicateur d'enregistrement avec icône."""
        self.set_recording_indicator(is_recording)
