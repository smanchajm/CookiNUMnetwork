from typing import Optional
import subprocess
import socket
import time
import requests
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.core.event_handler import events
from src.core.constants import mediamtx_path, mediamtx_config, streaming_rtmp_url


class StreamWaiterThread(QThread):
    """Thread to wait for stream availability without blocking UI."""

    stream_available = pyqtSignal()
    stream_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

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
                    if data.get("itemCount", 0) > 0:
                        print("Test: RTMP stream is available")
                        self.stream_available.emit()
                        return
                else:
                    print(f"Test: API returned status code {response.status_code}")
            except Exception as e:
                self.stream_error.emit(f"Error checking stream: {str(e)}")
                return
            time.sleep(0.5)  # Réduire l'intervalle de vérification


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
            sock.settimeout(0.5)  # Réduire le timeout
            result = sock.connect_ex(("localhost", 1935))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _wait_for_server(
        self, timeout: int = 5
    ) -> bool:  # Réduire le timeout par défaut
        """Wait for server to be ready with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            print("Test: Waiting for server to be ready")
            if self._is_server_running():
                print("Test: Server is now ready")
                return True
            time.sleep(0.5)  # Augmenter l'intervalle pour réduire la charge
        print("Test: Server failed to start within timeout period")
        return False

    def _start_waiting_for_stream(self):
        """
        Start waiting for stream in a separate thread.
        Used to wait for a stream to be available without blocking the UI thread.
        """
        if self.stream_waiter is not None:
            self.stream_waiter.stop()
            self.stream_waiter.wait()
            self.stream_waiter.deleteLater()

        self.stream_waiter = StreamWaiterThread(self)
        self.stream_waiter.stream_available.connect(self._on_stream_available)
        self.stream_waiter.stream_error.connect(self._on_stream_error)
        self.stream_waiter.start()

    def _on_stream_available(self):
        """Handle stream becoming available."""
        self.is_streaming = True
        events.streaming_started.emit()

    def _on_stream_error(self, error: str):
        """Handle stream error."""
        print(f"Test: Stream error: {error}")
        self.stop_mediamtx()
        events.streaming_error.emit(error)

    def start_mediamtx(self) -> bool:
        """Start the MediaMTX server."""
        try:
            if self.mediamtx_process is not None:
                print("Test: MediaMTX process already running")
                return True

            print("Starting MediaMTX server")
            # Vérifier si le processus est déjà en cours d'exécution
            if self._is_server_running():
                print("Test: MediaMTX server is already running on port 1935")
                self._start_waiting_for_stream()
                return True

            mediamtx_args = [mediamtx_path, mediamtx_config]
            print("Test: Launching MediaMTX")
            self.mediamtx_process = subprocess.Popen(
                mediamtx_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for server to be ready
            if not self._wait_for_server():
                print("Test: MediaMTX server failed to start within timeout")
                if self.mediamtx_process:
                    stdout, stderr = self.mediamtx_process.communicate()
                    print("Test: MediaMTX stdout:", stdout.decode())
                    print("Test: MediaMTX stderr:", stderr.decode())
                self.stop_mediamtx()
                events.streaming_error.emit(
                    "MediaMTX server failed to start within timeout"
                )
                return False

            # Start waiting for stream in background
            self._start_waiting_for_stream()
            return True
        except Exception as e:
            print(f"Test: Error starting MediaMTX: {str(e)}")
            events.streaming_error.emit(f"Error starting MediaMTX: {str(e)}")
            return False

    def stop_mediamtx(self) -> bool:
        """Stop the MediaMTX server."""
        try:
            if self.stream_waiter is not None:
                self.stream_waiter.stop()
                self.stream_waiter.wait()
                self.stream_waiter.deleteLater()
                self.stream_waiter = None

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
        return streaming_rtmp_url
