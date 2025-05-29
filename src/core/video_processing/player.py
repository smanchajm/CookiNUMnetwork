import sys
from abc import ABC, abstractmethod
from typing import Optional
import time
import threading

import cv2
import vlc

from src.core.logging_config import logger


class Player(ABC):
    """
    Abstract interface for a media player.
    Defines essential methods that any player must implement.
    """

    @abstractmethod
    def load(self, media_path):
        """
        Load a media file into the player.

        Args:
            media_path (str): Path to the media file.

        Returns:
            bool: True if loading succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def play(self):
        """Start playback."""
        pass

    @abstractmethod
    def pause(self):
        """Pause playback."""
        pass

    @abstractmethod
    def stop(self):
        """Stop playback."""
        pass

    @abstractmethod
    def rewind(self, seconds=10):
        """
        Rewind playback by X seconds.

        Args:
            seconds (int): Number of seconds to rewind (default: 10).
        """
        pass

    @abstractmethod
    def forward(self, seconds=10):
        """
        Forward playback by X seconds.

        Args:
            seconds (int): Number of seconds to forward (default: 10).
        """
        pass

    @abstractmethod
    def set_speed(self, speed):
        """
        Set playback speed.

        Args:
            speed (float): Playback speed.

        Returns:
            float: The applied playback speed.
        """
        pass

    @abstractmethod
    def decrease_speed(self):
        """
        Decrease playback speed by one level.

        Returns:
            float: The new playback speed.
        """
        pass

    @abstractmethod
    def seek(self, position):
        """
        Seek to a specific position.

        Args:
            position (float): Position as percentage (0.0 to 1.0).
        """
        pass

    @abstractmethod
    def get_time(self):
        """
        Get current position and total duration.

        Returns:
            tuple: (current_position, total_duration) in seconds.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Release player resources."""
        pass

    def set_video_output(self, win_id):
        """
        Configure video output for the player.
        This method is optional and can be implemented by child classes.

        Args:
            win_id: Window identifier for video display.
        """
        pass


class VLCPlayer(Player):
    """
    Concrete implementation of a player using VLC.
    """

    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.playback_speed = 1.0
        self.speed_levels = [0.25, 0.5, 0.75, 1.0]
        self.zoom_level = 1.0
        self.zoom_levels = [0, 2.0]

    def load(self, media_path):
        try:
            media = self.vlc_instance.media_new(media_path)
            self.media_player.set_media(media)
            return True
        except Exception:
            return False

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()
        # Reset zoom to default when stopping
        self.zoom_level = 1.0
        self.media_player.video_set_scale(self.zoom_level)

    def rewind(self, seconds=10):
        current_time = self.media_player.get_time() / 1000.0
        new_time = max(0, current_time - seconds) * 1000
        self.media_player.set_time(int(new_time))

    def forward(self, seconds=10):
        current_time = self.media_player.get_time() / 1000.0
        total_time = self.media_player.get_length() / 1000.0
        new_time = min(total_time, current_time + seconds) * 1000
        self.media_player.set_time(int(new_time))

    def set_speed(self, speed):
        if speed in self.speed_levels:
            self.playback_speed = speed
            self.media_player.set_rate(speed)
        return self.playback_speed

    def decrease_speed(self):
        try:
            current_index = self.speed_levels.index(self.playback_speed)
        except ValueError:
            current_index = self.speed_levels.index(1.0)

        next_index = (current_index - 1) % len(self.speed_levels)
        return self.set_speed(self.speed_levels[next_index])

    def seek(self, position):
        self.media_player.set_position(position)

    def get_time(self):
        current_time = self.media_player.get_time() / 1000.0
        total_time = self.media_player.get_length() / 1000.0
        return current_time, total_time

    def cleanup(self):
        self.stop()
        self.media_player.release()
        self.vlc_instance.release()

    def set_video_output(self, win_id):
        if sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(win_id))
        elif sys.platform == "win32":
            self.media_player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(win_id))

    def set_zoom(self, zoom_level):
        """
        Set the zoom level for the video.
        """
        logger.info(f"Setting zoom level to {zoom_level}")
        if zoom_level in self.zoom_levels:
            self.zoom_level = zoom_level
            self.media_player.video_set_scale(zoom_level)
        return self.zoom_level

    def cycle_zoom(self):
        """
        Cycle through available zoom levels.

        Returns:
            float: The new zoom level.
        """
        try:
            current_index = self.zoom_levels.index(self.zoom_level)
        except ValueError:
            current_index = 0

        next_index = (current_index + 1) % len(self.zoom_levels)
        return self.set_zoom(self.zoom_levels[next_index])


class OpenCVPlayer(Player):
    """
    Implementation of a player using OpenCV.
    """

    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_frame = None
        self.is_playing = False
        self.is_paused = False
        self.playback_speed = 1.0
        self.speed_levels = [0.25, 0.5, 0.75, 1.0]
        self.frame_delay = 0
        self._play_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.window_name = "OpenCV Player"

    def load(self, media_path):
        try:
            self.cap = cv2.VideoCapture(media_path)
            if not self.cap.isOpened():
                return False
            self._update_frame_delay()
            return True
        except Exception:
            return False

    def _update_frame_delay(self):
        """Update frame delay based on playback speed."""
        if self.cap is not None:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                self.frame_delay = int(1000 / (fps * self.playback_speed))

    def _play_loop(self):
        """Main playback loop."""
        while not self._stop_event.is_set() and self.is_playing:
            if not self.is_paused:
                ret, frame = self.cap.read()
                if not ret:
                    self.stop()
                    break
                self.current_frame = frame
                cv2.imshow(self.window_name, frame)
                cv2.waitKey(self.frame_delay)
            else:
                time.sleep(0.1)  # Prevent intensive loop during pause

    def play(self):
        if self.cap is None:
            return

        if not self.is_playing:
            self.is_playing = True
            self.is_paused = False
            self._stop_event.clear()
            self._play_thread = threading.Thread(target=self._play_loop)
            self._play_thread.start()

    def pause(self):
        self.is_paused = True

    def stop(self):
        self.is_playing = False
        self.is_paused = False
        self._stop_event.set()
        if self._play_thread is not None:
            self._play_thread.join()
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        cv2.destroyAllWindows()

    def rewind(self, seconds=10):
        if self.cap is None:
            return

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frames_to_rewind = int(seconds * fps)
        new_frame = max(0, current_frame - frames_to_rewind)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def forward(self, seconds=10):
        if self.cap is None:
            return

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frames_to_forward = int(seconds * fps)
        new_frame = min(total_frames, current_frame + frames_to_forward)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def set_speed(self, speed):
        if speed in self.speed_levels:
            self.playback_speed = speed
            self._update_frame_delay()
        return self.playback_speed

    def decrease_speed(self):
        try:
            current_index = self.speed_levels.index(self.playback_speed)
        except ValueError:
            current_index = self.speed_levels.index(1.0)

        next_index = (current_index - 1) % len(self.speed_levels)
        return self.set_speed(self.speed_levels[next_index])

    def seek(self, position):
        if self.cap is None:
            return

        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_position = int(position * total_frames)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)

    def get_time(self):
        if self.cap is None:
            return 0.0, 0.0

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        current_time = current_frame / fps if fps > 0 else 0.0
        total_time = total_frames / fps if fps > 0 else 0.0

        return current_time, total_time

    def cleanup(self):
        self.stop()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def set_video_output(self, win_id):
        pass
