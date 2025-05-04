from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt

from src.core.video_processing.media_service import MediaService
from src.ui.components.media_controls import MediaControls
from src.ui.utils.layouts import create_vbox_layout


class MediaReplaySection(QFrame):
    """
    Section du MediaPlayer dédiée au mode replay.
    Affiche la vidéo avec les contrôles de lecture.
    """

    def __init__(self, media_service: MediaService, parent=None):
        super().__init__(parent)
        self.setObjectName("media_replay_section")
        self.media_service = media_service

        self.setup_ui()

    def setup_ui(self):
        self.video_frame = QFrame()
        self.video_frame.setObjectName("video_frame")
        self.controls = MediaControls()

        # Créer le layout
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

    def add_tag_icon(self, timestamp, total_time):
        self.controls.on_add_tag(timestamp, total_time)
