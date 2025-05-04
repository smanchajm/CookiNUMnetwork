from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QMessageBox,
)

from src.core import constants
from src.core.camera_connection.gopro_service import GoProService
from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import ModeService, Mode
from src.core.video_processing.player import VLCPlayer
from src.core.video_processing.recording_service import RecordingService
from src.core.video_processing.tag_service import TagService
from src.ui.dialogs.gopro_connection_dialog import GoProConnectionDialog
from src.ui.dialogs.wifi_connection_dialog import WiFiConnectionDialog
from src.ui.services.dialog_service import DialogService
from src.ui.utils.layouts import create_hbox_layout
from src.ui.views.sidebar import Sidebar
from src.ui.views.media_player import MediaPlayer
from src.core.event_handler import events


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application CookiNUMnetwork.

    Cette classe orchestre l'interface utilisateur et coordonne les interactions
    entre les différents services (média, tags, enregistrement, etc.).
    Elle gère également les signaux et les événements de l'application.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CookiNUMnetwork")
        self.setWindowIcon(QIcon(constants.logo_path))

        # Initialiser les composants de base
        self.player = VLCPlayer()
        self.tag_manager = TagService()
        self.mode_manager = ModeService()
        self.recording_service = RecordingService()

        # Initialiser les services
        self.media_service = MediaService(self.player, self)
        self.gopro_service = GoProService(self)
        self.dialog_service = DialogService(self)

        # Initialiser les dialogues
        self.gopro_dialog = None
        self.wifi_dialog = None

        self.setup_ui()
        self.setup_connections()
        self.setup_mode_callbacks()

    def setup_ui(self):
        """Configure l'interface utilisateur principale."""
        # Créer le widget central
        central_widget = QWidget()

        # Créer les composants principaux
        self.sidebar = Sidebar()
        self.media_player = MediaPlayer(self.media_service)
        self.media_player.setObjectName("media_player_widget")

        # Créer le layout principal en utilisant la fonction helper
        content_layout = create_hbox_layout(
            widgets=[self.sidebar, self.media_player], spacing=0
        )

        # Définir les proportions
        content_layout.setStretchFactor(self.sidebar, 2)
        content_layout.setStretchFactor(self.media_player, 15)

        central_widget.setLayout(content_layout)
        self.setCentralWidget(central_widget)

        # Initialiser l'état des composants
        events.live_mode_changed.emit(self.mode_manager.is_live_mode)
        events.recording_state_changed.emit(self.recording_service.is_recording)

    def setup_connections(self):
        """Configure toutes les connexions de signaux entre les composants."""
        self._setup_sidebar_connections()
        self._setup_media_connections()
        self._setup_state_connections()

    def setup_mode_callbacks(self):
        """Configure les callbacks pour les changements de mode."""

        def on_mode_changed(old_mode: Mode, new_mode: Mode) -> None:
            """Callback appelé lors d'un changement de mode."""
            # Réinitialiser la vidéo lors du changement de mode
            self.media_service.reset_video()
            # Mettre à jour le media player si on est en mode live
            self.media_player.on_mode_changed(new_mode == Mode.LIVE)
            # Effacer les tags lors du passage en mode live
            if new_mode == Mode.LIVE:
                self.tag_manager.clear_tags()
            # Arrêter l'enregistrement lors du passage en mode replay
            elif new_mode == Mode.REVIEW and self.recording_service.is_recording:
                self.recording_service.stop_recording()

        self.mode_manager.add_transition_callback(on_mode_changed)

    def _setup_sidebar_connections(self):
        """Configure les connexions liées aux actions de la sidebar."""
        # Connexions des boutons d'action
        events.open_video_clicked.connect(self.media_service.open_video_file)
        events.start_recording_clicked.connect(self.recording_service.toggle_recording)
        events.connect_gopro_clicked.connect(self.dialog_service.show_gopro_dialog)
        events.connect_wifi_clicked.connect(self.dialog_service.show_wifi_dialog)
        events.live_mode_clicked.connect(self.mode_manager.toggle_live_mode)
        events.review_mode_clicked.connect(self.mode_manager.toggle_review_mode)

        # Connexions des tags
        events.add_tag_clicked.connect(self.on_add_tag)
        events.tag_selected.connect(self.on_tag_selected)

    def _setup_media_connections(self):
        """Configure les connexions liées au contrôle du média."""
        # Connexions des contrôles de lecture
        events.play_pause_signal.connect(self.media_service.toggle_play)
        events.rewind_signal.connect(lambda: self.media_service.rewind(10))
        events.forward_signal.connect(lambda: self.media_service.forward(10))
        events.seek_signal.connect(self.media_service.seek)
        events.slow_down_signal.connect(self.media_service.slow_down)

        # Connexions des mises à jour UI du lecteur
        events.play_state_changed.connect(self.media_player.on_play_state_changed)
        events.position_changed.connect(self.media_player.on_position_changed)

    def _setup_state_connections(self):
        """Configure les connexions liées aux changements d'état."""
        # Connexions du mode live
        events.live_mode_changed.connect(
            self.sidebar.action_section.on_live_mode_changed
        )
        events.live_mode_changed.connect(self.media_player.on_mode_changed)

        # Connexions de l'état d'enregistrement
        events.recording_state_changed.connect(
            self.sidebar.action_section.update_recording_state
        )
        events.recording_state_changed.connect(self.media_player.update_recording_state)

        # Connexions des tags
        events.tags_updated.connect(self.sidebar.tag_section.on_tags_changed)

    def on_add_tag(self) -> None:
        """Gère l'ajout d'un nouveau tag à la position courante."""
        current_time, _ = self.player.get_time()
        tag = self.tag_manager.create_and_add_tag(current_time)
        events.tags_updated.emit(self.tag_manager.get_tags())
        self.media_player.add_tag_marker_at(tag[0])  # tag[0] est le timestamp

    def on_tag_selected(self, timestamp_str: str) -> None:
        """
        Gère la sélection d'un tag et navigue vers sa position.

        Args:
            timestamp_str: Le timestamp du tag sélectionné au format string.
        """
        try:
            timestamp_seconds = float(timestamp_str)
            _, total_time = self.player.get_time()

            if total_time > 0:
                position_percent = timestamp_seconds / total_time
                self.media_service.seek(position_percent)
            else:
                self.dialog_service.show_error_message(
                    "Impossible de naviguer : durée de la vidéo inconnue"
                )
        except ValueError:
            self.dialog_service.show_error_message("Format de timestamp invalide")
