from PyQt6.QtWidgets import QFrame

from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import Mode
from src.ui.components.media_live_section import MediaLiveSection
from src.ui.components.media_replay_section import MediaReplaySection
from src.ui.utils.layouts import create_vbox_layout


class MediaPlayer(QFrame):
    """
    Widget lecteur média avec contrôles personnalisés.
    Gère l'affichage des sections live et replay.
    """

    def __init__(self, media_service: MediaService, parent=None):
        super().__init__(parent)
        self.setObjectName("media_player")
        self.media_service = media_service

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur du lecteur."""
        # Créer les sections
        self.live_section = MediaLiveSection()
        self.replay_section = MediaReplaySection(self.media_service)

        # Créer le layout principal
        main_layout = create_vbox_layout(
            widgets=[self.live_section, self.replay_section],
            spacing=0,
            margins=(0, 0, 0, 0),
        )
        self.setLayout(main_layout)

        # Initialiser l'affichage
        self._update_display(False)  # Mode review par défaut

    def on_play_state_changed(self, is_playing: bool) -> None:
        """Met à jour l'état de lecture dans la section replay."""
        self.replay_section.on_play_state_changed(is_playing)

    def on_position_changed(self, current_time: float, total_time: float) -> None:
        """Met à jour la position dans la section replay."""
        self.replay_section.on_position_changed(current_time, total_time)

    def on_mode_changed(self, is_live_mode: bool) -> None:
        """
        Met à jour l'affichage en fonction du mode.

        Args:
            is_live_mode: True si on passe en mode live, False pour le mode review.
        """
        self.media_service.reset_video()
        self._update_display(is_live_mode)

    def set_rtmp_connected(self, is_connected: bool) -> None:
        """Update RTMP connection state."""
        self.live_section.set_rtmp_connected(is_connected)

    def _update_display(self, is_live_mode: bool) -> None:
        """
        Met à jour l'affichage en fonction du mode.

        Args:
            is_live_mode: True pour afficher la section live, False pour la section replay.
        """
        if is_live_mode:
            self.live_section.show()
            self.replay_section.hide()
        else:
            self.live_section.hide()
            self.replay_section.show()

    def add_tag_marker_at(self, timestamp: float) -> None:
        """
        Ajoute un marqueur de tag à la position spécifiée.

        Args:
            timestamp: Le timestamp où ajouter le marqueur.
        """
        _, total_time = self.media_service.get_time()
        self.replay_section.add_tag_icon(timestamp, total_time)

    def set_recording_indicator(self, visible: bool) -> None:
        """Show or hide the recording indicator overlay."""
        self.live_section.set_recording_indicator(visible)

    def update_recording_state(self, is_recording: bool) -> None:
        """Affiche ou masque l'indicateur d'enregistrement avec icône."""
        self.set_recording_indicator(is_recording)
