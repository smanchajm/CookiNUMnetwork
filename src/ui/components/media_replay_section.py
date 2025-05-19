from PyQt6.QtWidgets import QFrame

from src.core.video_processing.media_service import MediaService
from src.ui.components.media_controls import MediaControls
from src.ui.utils.layouts import create_vbox_layout
from src.utils.resource_manager import ResourceManager


class MediaReplaySection(QFrame):
    """
    MediaPlayer section dedicated to replay mode.
    Displays video with controls.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("media_replay_section")

        self.setup_ui()

    def setup_ui(self):
        self.video_frame = QFrame()
        self.video_frame.setObjectName("video_frame")
        self.controls = MediaControls()

        main_layout = create_vbox_layout(
            widgets=[self.video_frame, self.controls], spacing=0, margins=(0, 0, 0, 0)
        )
        main_layout.setStretchFactor(self.video_frame, 1)

        self.setLayout(main_layout)

    def on_play_state_changed(self, is_playing):
        print(f"on_play_state_changed: {is_playing}")
        if is_playing:
            self.controls.play_pause_btn._setup_icon(
                ResourceManager.get_icon_path("pause.svg")
            )
        else:
            self.controls.play_pause_btn._setup_icon(
                ResourceManager.get_icon_path("play_arrow.svg")
            )
        self.controls.is_playing = is_playing

    def on_position_changed(self, current_time, total_time):
        self.controls.update_timeline(current_time, total_time)

        if total_time > 0:
            position_percent = (current_time / total_time) * 100
            self.controls.update_slider_position(position_percent)
