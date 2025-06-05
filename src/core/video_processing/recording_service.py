import threading
from datetime import datetime
from pathlib import Path

import cv2
from PyQt6.QtCore import QObject, QThread


from src.core.event_handler import events
from src.core.logging_config import logger
from src.utils.resource_manager import ResourceManager


class RecordingThread(QThread):
    """
    Thread handling the recording process.
    Manages FFmpeg process and file operations asynchronously.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True
        self._output_file = None
        self._cap = None
        self._writer = None
        self._record_thread = None
        self._start_time = None

    def start_recording(self):
        """Start the recording process."""
        try:
            # Create output directory if it doesn't exist
            video_path = ResourceManager.get_app_data_paths("videos")
            video_path.mkdir(parents=True, exist_ok=True)

            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._output_file = video_path / f"recording_{timestamp}.mp4"

            # Open RTMP stream
            logger.info(f"Opening RTMP stream: {ResourceManager.get_gopro_rtmp_url()}")
            self._cap = cv2.VideoCapture(ResourceManager.get_gopro_rtmp_url())
            if not self._cap.isOpened():
                raise Exception("Could not open video stream")

            # Get video properties
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self._cap.get(cv2.CAP_PROP_FPS))

            # Create video writer with MP4V codec
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # MP4V codec
            self._writer = cv2.VideoWriter(
                str(self._output_file), fourcc, fps, (width, height), True  # isColor
            )

            if not self._writer.isOpened():
                raise Exception("Could not create video writer")

            self._start_time = datetime.now()
            self._record_thread = threading.Thread(target=self._record_frames)
            self._record_thread.start()
            events.recording_started.emit(str(self._output_file))

        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            events.recording_error.emit(f"Error starting recording: {str(e)}")
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

        if self._output_file and Path(self._output_file).exists():
            events.recording_stopped.emit(str(self._output_file))

    def stop(self):
        """Stop the thread."""
        self._is_running = False
        self.stop_recording()
        self.wait()

    def get_recording_duration(self) -> float:
        """Get the current recording duration in seconds."""
        if self._start_time is None:
            return 0
        return (datetime.now() - self._start_time).total_seconds()


class RecordingService(QObject):
    """
    Service managing video recording.
    Centralizes recording state and notifies concerned sections.
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
                events.recording_started.disconnect()
                events.recording_stopped.disconnect()
                events.recording_error.disconnect()
            except (TypeError, RuntimeError):
                pass  # Ignore if signals were already disconnected
            self._recording_thread.deleteLater()

        # Create new thread
        self._recording_thread = RecordingThread(self)
        events.recording_started.connect(self._on_recording_started)
        events.recording_stopped.connect(self._on_recording_stopped)
        events.recording_error.connect(self._on_recording_error)

    @property
    def is_recording(self) -> bool:
        """Indicates if recording is in progress."""
        return self._is_recording

    @property
    def current_recording_path(self) -> str:
        """Get the path of the current recording file."""
        if self._recording_thread and self._is_recording:
            return str(self._recording_thread._output_file)
        return None

    def _on_recording_started(self, output_file: str):
        """Handle recording started event from thread."""
        logger.info(f"Recording started: {output_file}")
        self._is_recording = True
        events.recording_state_changed.emit(True)

    def _on_recording_stopped(self, output_file: str):
        """Handle recording stopped event from thread."""
        logger.info(f"Recording stopped and saved to: {output_file}")
        self._is_recording = False
        events.recording_state_changed.emit(False)
        # Reset thread after recording is stopped
        self._setup_recording_thread()

    def _on_recording_error(self, error: str):
        """Handle recording error event from thread."""
        logger.error(f"Recording error: {error}")
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
                    events.recording_started.disconnect()
                    events.recording_stopped.disconnect()
                    events.recording_error.disconnect()
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
                logger.error(f"Error during cleanup: {str(e)}")
            finally:
                self._is_recording = False
