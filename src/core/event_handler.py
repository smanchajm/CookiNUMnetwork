from PySide6.QtCore import Signal, QObject


class EventHandler(QObject):
    """Centralized event handler for the application Signals."""

    _instance = None

    # Live mode Signals
    live_mode_changed = Signal(bool)  # True for live mode, False for review mode

    # Recording Signals
    recording_state_changed = Signal(bool)  # True for recording, False for stopped
    recording_started = Signal(str)  # Path to the recording file
    recording_stopped = Signal(str)  # Path to the recording file
    recording_error = Signal(str)  # Error message

    # Tag management Signals
    tags_updated = Signal(list)  # List of all tags
    add_tag_clicked = Signal()
    tag_selected = Signal(str)
    request_tag_timestamp = Signal(int)  # Tag number requested by voice command
    delete_tag = Signal(str)

    # GoPro Signals
    connected = Signal()
    disconnected = Signal()
    connection_error = Signal(str)
    qrcode_created = Signal(str)

    # Streaming Signals
    streaming_started = Signal()
    streaming_stopped = Signal()
    streaming_error = Signal(str)
    streaming_status = Signal(str)

    # Media Signals
    media_loaded = Signal(str)
    media_loaded_total_time = Signal(float)
    media_error = Signal(str)
    play_state_changed = Signal(bool)
    toggle_play_Signal = Signal()
    media_ended = Signal()  # Signal emitted when media playback ends

    # Media controls Signals
    rewind_Signal = Signal()
    forward_Signal = Signal()
    play_pause_Signal = Signal()
    seek_Signal = Signal(float)
    slow_down_Signal = Signal()
    position_changed = Signal(float, float)

    # Sidebar actions Signals
    open_video_clicked = Signal()
    start_recording_clicked = Signal()
    connect_gopro_clicked = Signal()
    connect_wifi_clicked = Signal()
    live_mode_clicked = Signal()
    review_mode_clicked = Signal()
    load_last_video_clicked = Signal()

    # Mode transition Signals
    mode_changed = Signal(bool)  # bool: is_live_mode

    # Media playback Signals
    media_playback_started = Signal()
    media_playback_paused = Signal()
    media_playback_stopped = Signal()
    media_playback_error = Signal(str)

    # Progression Signals
    progress_updated = Signal(float)  # Progress as percentage (0-100)
    time_updated = Signal(int, int)  # (current position, total duration) in seconds

    # Speed Signals
    speed_changed = Signal(float)  # New playback speed

    # Application events
    application_closing = Signal()

    # Zoom Signals
    cycle_zoom_Signal = Signal()
    zoom_in_Signal = Signal()
    zoom_out_Signal = Signal()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._initialized = True


# Create a singleton of EventHandler
events = EventHandler()
