from typing import Optional
import subprocess
from PyQt6.QtCore import QObject

from src.core.event_handler import events
from src.core.constants import mediamtx_path, mediamtx_config


class StreamingService(QObject):
    """
    Service managing RTMP streaming with MediaMTX.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mediamtx_process: Optional[subprocess.Popen] = None
        self.is_streaming = False

    def start_mediamtx(self) -> bool:
        """Start the MediaMTX server."""
        try:
            if self.mediamtx_process is not None:
                return True

            # Démarrer MediaMTX avec la configuration existante
            self.mediamtx_process = subprocess.Popen(
                [mediamtx_path, mediamtx_config],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.is_streaming = True
            events.streaming_started.emit()
            return True
        except Exception as e:
            print(f"Test: Error starting MediaMTX: {str(e)}")
            events.streaming_error.emit(f"Error starting MediaMTX: {str(e)}")
            return False

    def stop_mediamtx(self) -> bool:
        """Stop the MediaMTX server."""
        try:
            if self.mediamtx_process is not None:
                self.mediamtx_process.terminate()
                self.mediamtx_process.wait()
                self.mediamtx_process = None
                self.is_streaming = False
                events.streaming_stopped.emit()
            return True
        except Exception as e:
            events.streaming_error.emit(f"Error stopping MediaMTX: {str(e)}")
            return False

    def get_stream_url(self) -> str:
        """Return the RTMP stream URL."""
        return "rtmp://localhost:1935/live"

    def get_player_url(self) -> str:
        """Return the player URL."""
        return "rtmp://localhost:1935/live"
