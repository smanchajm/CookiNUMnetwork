from PySide6.QtWidgets import QMainWindow

from src.core.camera_connection.gopro_service import GoProService
from src.core.event_handler import events
from src.core.keyboard_shortcuts_service import KeyboardShortcutsService
from src.core.logging_config import logger
from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import ModeService, Mode
from src.core.video_processing.player import VLCPlayer
from src.core.video_processing.recording_service import RecordingService
from src.core.video_processing.tag_service import TagService
from src.core.voice_recognition.voice_service import VoiceService
from src.ui.dialogs.dialog_service import DialogService


class MainController:
    """
    Controller for the CookiNUMnetwork application.

    This class handles all business logic and coordinates between different services.
    It acts as the bridge between the UI (MainWindow) and the core services.
    """

    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

        # Initialize base sections
        self.replay_player = VLCPlayer()
        self.tag_manager = TagService()
        self.mode_manager = ModeService()

        # Initialize services
        self.recording_service = RecordingService()
        self.media_service = MediaService(self.replay_player, parent=main_window)
        self.gopro_service = GoProService(parent=main_window)
        self.dialog_service = DialogService(parent=main_window)
        self.voice_service = VoiceService(parent=main_window)
        self.keyboard_shortcuts_service = KeyboardShortcutsService(parent=main_window)

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
        self.gopro_service.start_streaming()
        logger.info("Starting voice service")
        self.voice_service.start()
        logger.info("Voice service started")

    def setup_connections(self):
        """Configure all Signal connections between sections."""
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
                if self.recording_service.is_recording:
                    recording_path = self.recording_service.current_recording_path
                    self.tag_manager.current_video_path = recording_path
            else:  # REVIEW mode
                self.tag_manager.clear_tags()
                self.tag_manager.current_video_path = (
                    self.media_service.current_video_path
                )
                self.tag_manager.reload_tags()

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
        events.load_last_video_clicked.connect(
            self.media_service.load_last_recorded_video
        )

        # Tag connections
        events.add_tag_clicked.connect(self._on_add_tag_clicked)
        events.tag_selected.connect(self.on_tag_selected)
        events.request_tag_timestamp.connect(self._on_request_tag_timestamp)
        events.delete_tag.connect(self.tag_manager.delete_tag)

    def _setup_media_connections(self):
        """Configure connections for media control."""
        # Playback control connections
        events.play_pause_Signal.connect(self.media_service.toggle_play_pause)
        events.rewind_Signal.connect(lambda: self.media_service.rewind(10))
        events.forward_Signal.connect(lambda: self.media_service.forward(10))
        events.seek_Signal.connect(self.media_service.seek)
        events.slow_down_Signal.connect(self.media_service.slow_down)
        events.cycle_zoom_Signal.connect(self.media_service.cycle_zoom)
        events.zoom_in_Signal.connect(self.media_service.zoom_in)
        events.zoom_out_Signal.connect(self.media_service.zoom_out)

        events.position_changed.connect(
            self.main_window.media_player.on_position_changed
        )
        events.play_state_changed.connect(
            self.main_window.media_player.on_play_state_changed
        )

        # Load tags when a video is loaded
        events.media_loaded.connect(self.tag_manager.load_tags_for_video)
        events.media_loaded_total_time.connect(
            self.main_window.media_player.replay_section.controls.update_total_time
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

        # Recording state connections
        events.recording_state_changed.connect(
            self.main_window.sidebar.action_section.update_recording_state
        )
        events.recording_state_changed.connect(
            self.main_window.sidebar.logo_section.on_recording_state_changed
        )
        # Update video path when recording starts/stops
        events.recording_state_changed.connect(self._on_recording_state_changed)

        events.voice_command_recognized.connect(
            self.main_window.sidebar.logo_section.on_recording_state_changed
        )

        # Tag connections
        events.tags_updated.connect(
            self.main_window.sidebar.tag_section.update_tag_display
        )
        events.tags_updated.connect(
            self.main_window.media_player.replay_section.controls.on_tags_changed
        )

    def _on_recording_state_changed(self, is_recording: bool) -> None:
        """Handle recording state changes."""
        if self.mode_manager.get_mode() == Mode.LIVE:
            if is_recording:
                # When recording starts, set the video path and clear tags
                recording_path = self.recording_service.current_recording_path
                if recording_path:
                    self.tag_manager.current_video_path = recording_path
                    self.tag_manager.clear_tags()
            else:
                # When recording stops, clear the video path
                self.tag_manager.current_video_path = None

    def on_tag_selected(self, timestamp_str: str) -> None:
        """
        Handle tag selection and navigate to its position.

        Args:
            timestamp_str: Selected tag timestamp as string.
        """
        try:
            timestamp_seconds = float(timestamp_str)
            total_time = self.media_service.total_time

            if total_time > 0:
                position_percent = timestamp_seconds / total_time
                self.media_service.seek(position_percent)
            else:
                self.dialog_service.show_error_message(
                    "Cannot navigate: unknown video duration"
                )
        except ValueError:
            self.dialog_service.show_error_message("Invalid timestamp format")

    def _on_add_tag_clicked(self) -> None:
        """Handle add tag button click."""
        if self.mode_manager.get_mode() == Mode.LIVE:
            if self.recording_service.is_recording:
                self.tag_manager.add_tag_at_time(
                    self.recording_service._recording_thread.get_recording_duration()
                )
        else:
            self.tag_manager.add_tag_at_time(self.media_service.get_current_time()[0])

    def _on_request_tag_timestamp(self, tag_number: int) -> None:
        """
        Handle request for tag timestamp from voice command.

        Args:
            tag_number: The requested tag number (1-based index)
        """
        tags = self.tag_manager.get_tags()
        if tags and 0 <= tag_number - 1 < len(tags):
            # Get the timestamp of the selected tag
            timestamp = float(
                tags[tag_number - 1][0]
            )  # First element of the tuple is the timestamp
            events.tag_selected.emit(str(timestamp))
        else:
            logger.warning(f"Tag number {tag_number} not found")

    def cleanup(self):
        """Clean up all resources before application shutdown."""
        logger.info("Application closing, cleaning up resources...")

        if hasattr(self, "recording_service"):
            self.recording_service.cleanup()
        # if hasattr(self, "streaming_service"):
        #     self.streaming_service.stop_mediamtx()
        if hasattr(self, "media_service"):
            self.media_service.cleanup()
        if hasattr(self, "voice_service"):
            self.voice_service.stop()
        if hasattr(self, "gopro_service"):
            self.gopro_service.stop_streaming()

        logger.info("Cleanup completed")
