from PyQt6.QtWidgets import QFrame

from src.core.video_processing.media_service import MediaService
from src.core.video_processing.mode_service import Mode
from src.ui.components.media_live_section import MediaLiveSection
from src.ui.components.media_replay_section import MediaReplaySection
from src.ui.utils.layouts import create_vbox_layout


class MediaPlayer(QFrame):
    """
    Media player widget with custom controls.
    Manages display of live and replay sections.
    """

    def __init__(self, media_service: MediaService, parent=None):
        super().__init__(parent)
        self.setObjectName("media_player")
        self.media_service = media_service

        self.setup_ui()

    def setup_ui(self):
        self.live_section = MediaLiveSection()
        self.replay_section = MediaReplaySection(self.media_service)

        main_layout = create_vbox_layout(
            widgets=[self.live_section, self.replay_section],
            spacing=0,
            margins=(0, 0, 0, 0),
        )
        self.setLayout(main_layout)

    def on_play_state_changed(self, is_playing: bool) -> None:
        """Update playback state in the replay section."""
        self.replay_section.on_play_state_changed(is_playing)

    def on_position_changed(self, current_time: float, total_time: float) -> None:
        """Update position in the replay section."""
        self.replay_section.on_position_changed(current_time, total_time)

    def on_mode_changed(self, is_live_mode: bool) -> None:
        """
        Update display based on mode.
        """
        self.update_display(is_live_mode)

    def set_rtmp_connected(self, is_connected: bool) -> None:
        """Update RTMP connection state."""
        self.live_section.set_rtmp_connected(is_connected)

    def update_display(self, is_live_mode: bool) -> None:
        """
        Update display based on mode.
        """
        if is_live_mode:
            self.live_section.show()
            self.replay_section.hide()
        else:
            self.live_section.hide()
            self.replay_section.show()

    def add_tag_marker_at(self, current_time: float, total_time: float) -> None:
        """
        Add a tag marker at the specified position.

        Args:
            current_time: Timestamp where to add the marker.
            total_time: Total video duration.
        """
        self.replay_section.add_tag_icon(current_time, total_time)

    def set_recording_indicator(self, visible: bool) -> None:
        """Show or hide the recording indicator overlay."""
        self.live_section.set_recording_indicator(visible)

    def update_recording_state(self, is_recording: bool) -> None:
        """Show or hide the recording indicator with icon."""
        self.set_recording_indicator(is_recording)
