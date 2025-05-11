from PyQt6.QtWidgets import QMainWindow
from src.core.camera_connection.gopro_service import GoProService
from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import ModeService, Mode
from src.core.video_processing.player import VLCPlayer
from src.core.video_processing.recording_service import RecordingService
from src.core.video_processing.tag_service import TagService
from src.core.streaming.streaming_service import StreamingService
from src.ui.dialogs.dialog_service import DialogService
from src.core.event_handler import events


class MainController:
    """
    Controller for the CookiNUMnetwork application.

    This class handles all business logic and coordinates between different services.
    It acts as the bridge between the UI (MainWindow) and the core services.
    """

    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

        # Initialize base components
        self.replay_player = VLCPlayer()
        self.tag_manager = TagService()
        self.mode_manager = ModeService()

        # Initialize services
        self.streaming_service = StreamingService()
        self.recording_service = RecordingService()
        self.media_service = MediaService(self.replay_player, parent=main_window)
        self.gopro_service = GoProService(parent=main_window)
        self.dialog_service = DialogService(parent=main_window)

        # Set video output for replay player
        if self.main_window.media_player.replay_section.video_frame.winId():
            self.media_service.set_video_output(
                self.main_window.media_player.replay_section.video_frame.winId()
            )

        # Initialize dialogs
        self.gopro_dialog = None
        self.wifi_dialog = None

        self.setup_connections()
        self.setup_mode_callbacks()

        # Initialize services after all connections are established
        self.mode_manager.initialize()
        events.recording_state_changed.emit(self.recording_service.is_recording)
        self.gopro_service.start_streaming()

    def setup_connections(self):
        """Configure all signal connections between components."""
        self._setup_application_connections()
        self._setup_sidebar_connections()
        self._setup_media_connections()
        self._setup_state_connections()

    def _setup_application_connections(self):
        """Configure connections for application-level events."""
        events.application_closing.connect(self.cleanup)

    def setup_mode_callbacks(self):
        """Configure callbacks for mode changes."""

        def on_mode_changed(old_mode: Mode, new_mode: Mode) -> None:
            """Callback called when mode changes."""
            self.media_service.pause()
            if new_mode == Mode.LIVE:
                self.tag_manager.clear_tags()

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

        events.position_changed.connect(
            self.main_window.media_player.on_position_changed
        )
        events.play_state_changed.connect(
            self.main_window.media_player.on_play_state_changed
        )

    def _setup_state_connections(self):
        """Configure connections for state changes."""
        # Connect streaming state changes
        events.streaming_started.connect(
            self.main_window.media_player.live_section.on_streaming_started
        )
        events.streaming_stopped.connect(
            self.main_window.media_player.live_section.on_streaming_stopped
        )

        # Live mode connections
        events.live_mode_changed.connect(
            self.main_window.sidebar.action_section.on_live_mode_changed
        )
        events.live_mode_changed.connect(self.main_window.media_player.update_display)

        # Recording state connections - only update UI
        events.recording_state_changed.connect(
            self.main_window.sidebar.action_section.update_recording_state
        )
        events.recording_state_changed.connect(
            self.main_window.media_player.update_recording_state
        )

        # Tag connections
        events.tags_updated.connect(
            self.main_window.sidebar.tag_section.on_tags_changed
        )

    def on_add_tag(self) -> None:
        """Handle adding a new tag at the current position."""
        current_time, total_time = self.media_service.get_current_time()
        self.tag_manager.create_and_add_tag(current_time)
        self.main_window.media_player.add_tag_marker_at(current_time, total_time)

    def on_tag_selected(self, timestamp_str: str) -> None:
        """
        Handle tag selection and navigate to its position.

        Args:
            timestamp_str: Selected tag timestamp as string.
        """
        try:
            timestamp_seconds = float(timestamp_str)
            _, total_time = self.replay_player.get_time()

            if total_time > 0:
                position_percent = timestamp_seconds / total_time
                self.media_service.seek(position_percent)
            else:
                self.dialog_service.show_error_message(
                    "Cannot navigate: unknown video duration"
                )
        except ValueError:
            self.dialog_service.show_error_message("Invalid timestamp format")

    def cleanup(self):
        """Clean up all resources before application shutdown."""
        print("Test: Application closing, cleaning up resources...")

        if hasattr(self, "recording_service"):
            self.recording_service.cleanup()
        if hasattr(self, "streaming_service"):
            self.streaming_service.stop_mediamtx()
        if hasattr(self, "media_service"):
            self.media_service.cleanup()

        print("Test: Cleanup completed")
