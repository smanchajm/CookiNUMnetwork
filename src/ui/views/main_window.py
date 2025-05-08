from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
)

from src.core import constants
from src.core.camera_connection.gopro_service import GoProService
from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import ModeService, Mode
from src.core.video_processing.player import VLCPlayer
from src.core.video_processing.recording_service import RecordingService
from src.core.video_processing.tag_service import TagService
from src.ui.services.dialog_service import DialogService
from src.ui.utils.layouts import create_hbox_layout
from src.ui.views.sidebar import Sidebar
from src.ui.views.media_player import MediaPlayer
from src.core.event_handler import events


class MainWindow(QMainWindow):
    """
    Main window of the CookiNUMnetwork application.

    This class orchestrates the user interface and coordinates interactions
    between different services (media, tags, recording, etc.).
    It also handles application signals and events.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CookiNUMnetwork")
        self.setWindowIcon(QIcon(constants.logo_path))

        # Initialize base components
        self.player = VLCPlayer()
        self.tag_manager = TagService()
        self.mode_manager = ModeService()
        self.recording_service = RecordingService()

        # Initialize services
        self.media_service = MediaService(self.player, self)
        self.gopro_service = GoProService(self)
        self.dialog_service = DialogService(self)

        # Initialize dialogs
        self.gopro_dialog = None
        self.wifi_dialog = None

        self.setup_ui()
        self.setup_connections()
        self.setup_mode_callbacks()

        # Initialize services after all connections are established
        self.mode_manager.initialize()
        events.recording_state_changed.emit(self.recording_service.is_recording)

    def setup_ui(self):
        """Configure the main user interface."""
        central_widget = QWidget()

        self.sidebar = Sidebar()
        self.media_player = MediaPlayer(self.media_service)
        self.media_player.setObjectName("media_player_widget")

        content_layout = create_hbox_layout(
            widgets=[self.sidebar, self.media_player], spacing=0
        )

        content_layout.setStretchFactor(self.sidebar, 2)
        content_layout.setStretchFactor(self.media_player, 15)

        central_widget.setLayout(content_layout)
        self.setCentralWidget(central_widget)

    def setup_connections(self):
        """Configure all signal connections between components."""
        self._setup_sidebar_connections()
        self._setup_media_connections()
        self._setup_state_connections()

    def setup_mode_callbacks(self):
        """Configure callbacks for mode changes."""

        def on_mode_changed(old_mode: Mode, new_mode: Mode) -> None:
            """Callback called when mode changes."""
            self.media_service.reset_video()
            if new_mode == Mode.LIVE:
                self.tag_manager.clear_tags()
                self.gopro_service.start_streaming()

        self.mode_manager.add_transition_callback(on_mode_changed)

    def _setup_sidebar_connections(self):
        """Configure connections for sidebar actions."""
        # Action button connections
        events.open_video_clicked.connect(self.media_service.open_video_file)
        events.start_recording_clicked.connect(self.recording_service.toggle_recording)
        events.connect_gopro_clicked.connect(self.dialog_service.show_gopro_dialog)
        events.connect_wifi_clicked.connect(self.dialog_service.show_wifi_dialog)
        events.live_mode_clicked.connect(self.mode_manager.toggle_live_mode)
        events.review_mode_clicked.connect(self.mode_manager.toggle_review_mode)

        # Tag connections
        events.add_tag_clicked.connect(self.on_add_tag)
        events.tag_selected.connect(self.on_tag_selected)

    def _setup_media_connections(self):
        """Configure connections for media control."""
        # Playback control connections
        events.play_pause_signal.connect(self.media_service.toggle_play)
        events.rewind_signal.connect(lambda: self.media_service.rewind(10))
        events.forward_signal.connect(lambda: self.media_service.forward(10))
        events.seek_signal.connect(self.media_service.seek)
        events.slow_down_signal.connect(self.media_service.slow_down)

        # Player UI update connections
        events.play_state_changed.connect(self.media_player.on_play_state_changed)
        events.position_changed.connect(self.media_player.on_position_changed)

        # Streaming connections
        events.streaming_started.connect(
            self.media_player.media_live_section.on_streaming_started
        )
        events.streaming_stopped.connect(
            self.media_player.media_live_section.on_streaming_stopped
        )
        events.streaming_error.connect(
            self.media_player.media_live_section.on_streaming_error
        )

    def _setup_state_connections(self):
        """Configure connections for state changes."""
        # Live mode connections
        events.live_mode_changed.connect(
            self.sidebar.action_section.on_live_mode_changed
        )
        events.live_mode_changed.connect(self.media_player.update_display)

        # Recording state connections
        events.recording_state_changed.connect(
            self.sidebar.action_section.update_recording_state
        )
        events.recording_state_changed.connect(self.media_player.update_recording_state)

        # Tag connections
        events.tags_updated.connect(self.sidebar.tag_section.on_tags_changed)

    def on_add_tag(self) -> None:
        """Handle adding a new tag at the current position."""
        current_time, total_time = self.media_service.get_current_time()
        self.tag_manager.create_and_add_tag(current_time)
        self.media_player.add_tag_marker_at(current_time, total_time)

    def on_tag_selected(self, timestamp_str: str) -> None:
        """
        Handle tag selection and navigate to its position.

        Args:
            timestamp_str: Selected tag timestamp as string.
        """
        try:
            timestamp_seconds = float(timestamp_str)
            _, total_time = self.player.get_time()

            if total_time > 0:
                position_percent = timestamp_seconds / total_time
                self.media_service.seek(position_percent)
            else:
                self.dialog_service.show_error_message(
                    "Cannot navigate: unknown video duration"
                )
        except ValueError:
            self.dialog_service.show_error_message("Invalid timestamp format")
