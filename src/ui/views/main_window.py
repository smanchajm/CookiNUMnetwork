from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QMessageBox,
)

from src.core import constants
from src.core.camera_connection.gopro_service import GoProService
from src.core.video_processing.media_service import MediaService
from src.core.video_processing.player import VLCPlayer, OpenCVPlayer
from src.core.video_processing.recording_service import RecordingService
from src.core.video_processing.tag_service import TagService
from src.ui.dialogs.gopro_connection_dialog import GoProConnectionDialog
from src.ui.dialogs.wifi_connection_dialog import WiFiConnectionDialog
from src.ui.utils.layouts import create_hbox_layout
from src.ui.views.sidebar import Sidebar
from src.ui.views.media_player import MediaPlayer
from src.core.event_handler import events


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CookiNUMnetwork")
        self.setWindowIcon(QIcon(constants.logo_path))

        # Initialiser les composants de base
        self.player = VLCPlayer()
        self.tag_manager = TagService()

        # Initialiser les services
        self.media_service = MediaService(self.player, self)
        self.recording_service = RecordingService(self)
        self.gopro_service = GoProService(self)

        # Initialiser les dialogues
        self.gopro_dialog = None
        self.wifi_dialog = None

        # init state
        self.is_live_mode = False
        self.is_recording = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
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

        # init state
        events.live_mode_changed.emit(self.is_live_mode)
        events.recording_state_changed.emit(self.is_recording)

    def setup_connections(self):
        """Configure toutes les connexions de signaux entre les composants."""
        self._setup_sidebar_connections()
        self._setup_media_connections()
        self._setup_state_connections()

    def _setup_sidebar_connections(self):
        """Configure les connexions liées aux actions de la sidebar."""
        # Connexions des boutons d'action
        events.open_video_clicked.connect(self.media_service.open_video_file)
        events.start_recording_clicked.connect(self.toggle_recording)
        events.connect_gopro_clicked.connect(self.show_gopro_dialog)
        events.connect_wifi_clicked.connect(self.show_wifi_dialog)
        events.live_mode_clicked.connect(self.toggle_live_mode)
        events.review_mode_clicked.connect(self.toggle_review_mode)

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
        events.live_mode_changed.connect(self.media_player.on_live_mode_changed)

        # Connexions de l'état d'enregistrement
        events.recording_state_changed.connect(
            self.sidebar.action_section.update_recording_state
        )
        events.recording_state_changed.connect(self.media_player.update_recording_state)

        # Connexions des tags
        events.tags_updated.connect(self.sidebar.tag_section.on_tags_changed)

    def show_error_message(self, message):
        QMessageBox.critical(self, "Erreur", message)

    def on_add_tag(self):
        current_time, total_time = self.player.get_time()
        new_tag_name = f"Tag {len(self.tag_manager.get_tags()) + 1}"
        self.tag_manager.add_tag(new_tag_name, current_time)
        events.tags_updated.emit(self.tag_manager.get_tags())
        self.media_player.add_tag_icon(current_time, total_time)

    def show_gopro_dialog(self):
        """Affiche le dialogue de connexion GoPro."""
        if self.gopro_dialog is None:
            self.gopro_dialog = GoProConnectionDialog(self)

        self.gopro_dialog.show()

    def show_wifi_dialog(self):
        """Affiche le dialogue de configuration WiFi pour GoPro."""
        if self.wifi_dialog is None:
            self.wifi_dialog = WiFiConnectionDialog(self)

        self.wifi_dialog.show()

    def on_tag_selected(self, timestamp_str):
        """Handle tag selection and seek to the corresponding timestamp."""
        try:
            timestamp_seconds = float(timestamp_str)

            _, total_time = self.player.get_time()

            if total_time > 0:
                position_percent = timestamp_seconds / total_time
                self.media_service.seek(position_percent)
            else:
                self.show_error_message(
                    "Impossible de naviguer : durée de la vidéo inconnue"
                )
        except ValueError:
            self.show_error_message("Format de timestamp invalide")

    def toggle_live_mode(self):
        """Bascule entre le mode review et le mode live."""
        self.is_live_mode = True
        events.live_mode_changed.emit(self.is_live_mode)
        # self.sidebar.action_section.buttons["live_mode_btn"].setProperty("active", True)
        # self.sidebar.action_section.buttons["review_mode_btn"].setProperty(
        #     "active", False
        # )

        self.sidebar.action_section.buttons["live_mode_btn"].setStyleSheet(
            "background-color: #faebbe;"
        )
        self.sidebar.action_section.buttons["review_mode_btn"].setStyleSheet(
            "background-color: #f9fafb"
        )
        if self.is_live_mode:
            # TODO: Implémenter la connexion au flux GoPro
            pass
            # self.media_player.show_live_message("Connexion au flux GoPro en cours...")
        else:
            pass
            # Arrêter le flux live si actif
            # self.media_service.stop_live_stream()

    def toggle_review_mode(self):
        """Bascule entre le mode review et le mode live."""
        self.is_live_mode = False
        self.sidebar.action_section.buttons["live_mode_btn"].setStyleSheet(
            "background-color: #f9fafb"
        )
        self.sidebar.action_section.buttons["review_mode_btn"].setStyleSheet(
            "background-color: #faebbe;"
        )
        events.live_mode_changed.emit(self.is_live_mode)

    def toggle_recording(self):
        """Bascule l'état d'enregistrement."""
        if self.is_recording:
            self.recording_service.stop_recording()
        else:
            self.recording_service.start_recording()
        self.is_recording = not self.is_recording
        events.recording_state_changed.emit(self.is_recording)
