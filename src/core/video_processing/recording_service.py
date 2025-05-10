from PyQt6.QtCore import QObject, QThread, pyqtSignal
import os
from datetime import datetime
import cv2
import threading

from src.core.event_handler import events
from src.core.constants import video_files_path, streaming_rtmp_url


class RecordingThread(QThread):
    """
    Thread handling the recording process.
    Manages FFmpeg process and file operations asynchronously.
    """

    recording_started = pyqtSignal(str)  # Emits output file path
    recording_stopped = pyqtSignal(str)  # Emits output file path
    recording_error = pyqtSignal(str)  # Emits error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True
        self._output_file = None
        self._cap = None
        self._writer = None
        self._record_thread = None

    def start_recording(self):
        """Start the recording process."""
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists(video_files_path):
                os.makedirs(video_files_path)

            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._output_file = os.path.join(
                video_files_path, f"recording_{timestamp}.mp4"
            )

            # Open RTMP stream
            self._cap = cv2.VideoCapture(streaming_rtmp_url)
            if not self._cap.isOpened():
                raise Exception("Could not open video stream")

            # Get video properties
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self._cap.get(cv2.CAP_PROP_FPS))

            # Create video writer with H.264 codec
            fourcc = cv2.VideoWriter_fourcc(*"avc1")  # H.264 codec
            self._writer = cv2.VideoWriter(
                self._output_file, fourcc, fps, (width, height), True  # isColor
            )

            if not self._writer.isOpened():
                raise Exception("Could not create video writer")

            self._record_thread = threading.Thread(target=self._record_frames)
            self._record_thread.start()
            self.recording_started.emit(self._output_file)

        except Exception as e:
            self.recording_error.emit(f"Error starting recording: {str(e)}")
            if self._cap:
                self._cap.release()
            if self._writer:
                self._writer.release()

    def _record_frames(self):
        while self._is_running and self._cap is not None and self._writer is not None:
            ret, frame = self._cap.read()
            if ret:
                self._writer.write(frame)
            else:
                break

    def stop_recording(self):
        """Stop the recording process cleanly."""
        self._is_running = False
        if self._record_thread:
            self._record_thread.join()

        if self._writer:
            self._writer.release()
            self._writer = None

        if self._cap:
            self._cap.release()
            self._cap = None

        if self._output_file and os.path.exists(self._output_file):
            self.recording_stopped.emit(self._output_file)

    def stop(self):
        """Stop the thread."""
        self._is_running = False
        self.stop_recording()
        self.wait()


class RecordingService(QObject):
    """
    Service managing video recording.
    Centralizes recording state and notifies concerned components.
    Handles RTMP stream recording when streaming is active.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_recording = False
        self._recording_thread = None
        self._setup_recording_thread()

    def _setup_recording_thread(self):
        """Setup a new recording thread and connect its signals."""
        if self._recording_thread is not None:
            # Disconnect old signals
            try:
                self._recording_thread.recording_started.disconnect()
                self._recording_thread.recording_stopped.disconnect()
                self._recording_thread.recording_error.disconnect()
            except (TypeError, RuntimeError):
                pass  # Ignore if signals were already disconnected
            self._recording_thread.deleteLater()

        # Create new thread
        self._recording_thread = RecordingThread(self)
        self._recording_thread.recording_started.connect(self._on_recording_started)
        self._recording_thread.recording_stopped.connect(self._on_recording_stopped)
        self._recording_thread.recording_error.connect(self._on_recording_error)

    @property
    def is_recording(self) -> bool:
        """Indicates if recording is in progress."""
        return self._is_recording

    def _on_recording_started(self, output_file: str):
        """Handle recording started event from thread."""
        print(f"Recording started: {output_file}")
        self._is_recording = True
        events.recording_state_changed.emit(True)

    def _on_recording_stopped(self, output_file: str):
        """Handle recording stopped event from thread."""
        print(f"Recording stopped and saved to: {output_file}")
        self._is_recording = False
        events.recording_state_changed.emit(False)
        # Reset thread after recording is stopped
        self._setup_recording_thread()

    def _on_recording_error(self, error: str):
        """Handle recording error event from thread."""
        print(f"Recording error: {error}")
        self._is_recording = False
        events.recording_state_changed.emit(False)
        # Reset thread after error
        self._setup_recording_thread()

    def start_recording(self):
        """Start the recording process."""
        if not self._is_recording:
            self._recording_thread.start_recording()

    def stop_recording(self):
        """Stop the recording process."""
        if self._is_recording and self._recording_thread:
            self._recording_thread.stop_recording()

    def toggle_recording(self) -> None:
        """
        Toggle recording state.
        """
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def cleanup(self):
        """Clean up resources before application exit."""
        if self._recording_thread:
            try:
                # Disconnect signals first
                try:
                    self._recording_thread.recording_started.disconnect()
                    self._recording_thread.recording_stopped.disconnect()
                    self._recording_thread.recording_error.disconnect()
                except (TypeError, RuntimeError):
                    pass  # Ignore if signals were already disconnected

                # Stop recording if active
                if self._is_recording:
                    self._recording_thread.stop_recording()

                # Stop and wait for thread
                self._recording_thread.stop()
                self._recording_thread.wait()

                # Clean up thread
                self._recording_thread.deleteLater()
                self._recording_thread = None

            except Exception as e:
                print(f"Error during cleanup: {str(e)}")
            finally:
                self._is_recording = False
