from PyQt6.QtCore import pyqtSignal, QObject


class EventHandler(QObject):
    """Centralized event handler for the application signals."""

    _instance = None

    # Live mode signals
    live_mode_changed = pyqtSignal(bool)  # True for live mode, False for review mode

    # Recording signals
    recording_state_changed = pyqtSignal(bool)  # True for recording, False for stopped

    # Tag management signals
    tags_updated = pyqtSignal(list)  # List of all tags

    # GoPro signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_error = pyqtSignal(str)
    qrcode_created = pyqtSignal(str)

    # Streaming signals
    streaming_started = pyqtSignal()
    streaming_stopped = pyqtSignal()
    streaming_error = pyqtSignal(str)
    streaming_status = pyqtSignal(str)

    # Media signals
    media_loaded = pyqtSignal(str)
    media_error = pyqtSignal(str)
    play_state_changed = pyqtSignal(bool)
    media_ended = pyqtSignal()  # Signal emitted when media playback ends

    # Media controls signals
    rewind_signal = pyqtSignal()
    forward_signal = pyqtSignal()
    play_pause_signal = pyqtSignal(bool)
    seek_signal = pyqtSignal(float)
    slow_down_signal = pyqtSignal()
    position_changed = pyqtSignal(float, float)

    # Sidebar actions signals
    open_video_clicked = pyqtSignal()
    start_recording_clicked = pyqtSignal()
    connect_gopro_clicked = pyqtSignal()
    connect_wifi_clicked = pyqtSignal()
    live_mode_clicked = pyqtSignal()
    review_mode_clicked = pyqtSignal()

    # Sidebar tags signals
    add_tag_clicked = pyqtSignal()
    tag_selected = pyqtSignal(str)

    # Mode transition signals
    mode_changed = pyqtSignal(bool)  # bool: is_live_mode

    # Media playback signals
    media_playback_started = pyqtSignal()
    media_playback_paused = pyqtSignal()
    media_playback_stopped = pyqtSignal()
    media_playback_error = pyqtSignal(str)

    # Progression signals
    progress_updated = pyqtSignal(float)  # Progress as percentage (0-100)
    time_updated = pyqtSignal(int, int)  # (current position, total duration) in seconds

    # Speed signals
    speed_changed = pyqtSignal(float)  # New playback speed

    # Recording signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    recording_error = pyqtSignal(str)

    # Application events
    application_closing = pyqtSignal()

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
