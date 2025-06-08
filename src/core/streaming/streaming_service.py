import requests
import subprocess
import socket
import time
import threading
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.event_handler import events
from src.core.logging_config import logger
from src.utils.resource_manager import ResourceManager


class StreamWaiterThread(threading.Thread):
    """Thread to wait for stream availability without blocking UI."""

    def __init__(self, parent=None):
        super().__init__(daemon=True)
        self._is_running = True
        self._was_streaming = False
        self._parent = parent

    def stop(self):
        """Stop the thread."""
        self._is_running = False

    def run(self):
        """Wait for stream to be available."""
        while self._is_running:
            try:
                response = requests.get("http://localhost:9997/v3/rtmpconns/list")
                if response.status_code == 200:
                    data = response.json()
                    # Check if there are any active RTMP connections
                    has_stream = data.get("itemCount", 0) > 0

                    if has_stream and not self._was_streaming:
                        logger.info("RTMP stream is available")
                        self._was_streaming = True
                        events.streaming_started.emit()
                    elif not has_stream and self._was_streaming:
                        logger.info("RTMP stream is no longer available")
                        self._was_streaming = False
                        events.streaming_stopped.emit()
                else:
                    logger.warning(f"API returned status code {response.status_code}")
            except Exception as e:
                logger.error(f"Error checking stream: {str(e)}")
                events.streaming_error.emit(f"Error checking stream: {str(e)}")
                return
            time.sleep(0.5)  # Reduce check interval


class StreamingService(QObject):
    """
    Service managing RTMP streaming with MediaMTX.
    Handles server lifecycle and stream availability monitoring.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mediamtx_process: Optional[subprocess.Popen] = None
        self.is_streaming = False
        self.stream_waiter: Optional[StreamWaiterThread] = None

    def _is_server_running(self) -> bool:
        """Check if MediaMTX server is running and responding."""
        try:
            # Try to connect to the RTMP port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Reduce timeout
            result = sock.connect_ex(("localhost", 1935))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _wait_for_server(self, timeout: int = 5) -> bool:  # Reduce default timeout
        """Wait for server to be ready with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            logger.info("Waiting for server to be ready")
            if self._is_server_running():
                logger.info("Server is now ready")
                return True
            time.sleep(0.5)  # Increase interval to reduce load
        logger.error("Server failed to start within timeout period")
        return False

    def _start_waiting_for_stream(self):
        """
        Start waiting for stream in a separate thread.
        Used to wait for a stream to be available without blocking the UI thread.
        """
        if self.stream_waiter is not None:
            self.stream_waiter.stop()
            if self.stream_waiter.is_alive():
                self.stream_waiter.join(timeout=2.0)
            self.stream_waiter = None

        self.stream_waiter = StreamWaiterThread(self)
        self.stream_waiter.start()

    def _on_stream_available(self):
        """Handle stream becoming available."""
        self.is_streaming = True
        events.streaming_started.emit()

    def _on_stream_stopped(self):
        """Handle stream becoming unavailable."""
        self.is_streaming = False
        events.streaming_stopped.emit()

    def _on_stream_error(self, error: str):
        """Handle stream error."""
        logger.error(f"Stream error: {error}")
        self.is_streaming = False
        events.streaming_error.emit(error)
        self.stop_mediamtx()

    def start_mediamtx(self) -> bool:
        """Start the MediaMTX server."""
        try:
            if self.mediamtx_process is not None:
                logger.info("MediaMTX process already running")
                return True

            logger.info("Starting MediaMTX server")
            # Check if process is already running
            if self._is_server_running():
                logger.info("MediaMTX server is already running on port 1935")
                self._start_waiting_for_stream()
                return True

            logger.info("Launching MediaMTX")
            self.mediamtx_process = subprocess.Popen(
                ResourceManager.get_mediamtx_args(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for server to be ready
            if not self._wait_for_server():
                logger.error("MediaMTX server failed to start within timeout")
                if self.mediamtx_process:
                    stdout, stderr = self.mediamtx_process.communicate()
                    logger.error(f"MediaMTX stdout: {stdout.decode()}")
                    logger.error(f"MediaMTX stderr: {stderr.decode()}")
                self.stop_mediamtx()
                events.streaming_error.emit(
                    "MediaMTX server failed to start within timeout"
                )
                return False

            # Start waiting for stream in background
            self._start_waiting_for_stream()
            return True
        except Exception as e:
            logger.error(f"Error starting MediaMTX: {str(e)}")
            events.streaming_error.emit(f"Error starting MediaMTX: {str(e)}")
            return False

    def stop_mediamtx(self) -> bool:
        """Stop the MediaMTX server."""
        try:
            if self.stream_waiter is not None:
                self.stream_waiter.stop()
                if self.stream_waiter.is_alive():
                    self.stream_waiter.join(timeout=2.0)
                self.stream_waiter = None

            if self.mediamtx_process is not None:
                self.mediamtx_process.terminate()
                self.mediamtx_process.wait()
                self.mediamtx_process = None
                self.is_streaming = False
                events.streaming_stopped.emit()
                return True
            return True
        except Exception as e:
            logger.error(f"Error stopping MediaMTX: {str(e)}")
            events.streaming_error.emit(f"Error stopping MediaMTX: {str(e)}")
            return False

    def get_stream_url(self) -> str:
        """Return the RTMP stream URL."""
        return ResourceManager.get_gopro_rtmp_url()
