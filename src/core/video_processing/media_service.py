from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QFileDialog
import os

from src.core.constants import video_files_path
from src.core.video_processing.player import Player
from src.core.event_handler import events


class MediaService(QObject):
    """
    Service de gestion des médias qui gère la logique d'ouverture de fichiers et de lecture.
    Sépare la logique métier de l'interface utilisateur.
    """

    def __init__(self, player: Player, parent=None):
        super().__init__(parent)
        self.player = player
        self.is_playing = False
        self.loop_enabled = True  # Enable loop by default
        self.current_video_path = None
        self.total_time = 0  # Store total time as class attribute

        # Timer pour mettre à jour la position
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._update_position)
        self.timer.start()

        events.media_loaded.connect(self.load_media)

    def open_video_file(self, parent_widget=None, start_dir=video_files_path):
        """
        Open a dialog to select a video file.
        """
        if start_dir is None:
            start_dir = os.path.expanduser("~")
        elif not os.path.exists(start_dir):
            start_dir = os.path.expanduser("~")

        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Ouvrir une vidéo",
            start_dir,
            "Fichiers vidéo (*.mp4 *.avi *.mkv *.mov);;Tous les fichiers (*.*)",
        )

        if file_path:
            if os.path.exists(file_path):
                events.media_loaded.emit(file_path)
                return file_path
            else:
                error_msg = f"Le fichier {file_path} n'existe pas."
                events.media_error.emit(error_msg)
                return None

        return None

    def load_media(self, path):
        if self.player.load(path):
            self.current_video_path = path
            # Start playing to ensure media is fully loaded
            self.play()
            # Get total time after a short delay to ensure it's available
            QTimer.singleShot(1000, self._get_total_time)
            return True
        else:
            self.pause()
            events.media_error.emit(f"Impossible de charger le fichier: {path}")
            return False

    def _get_total_time(self):
        """Get the total time after media is loaded and playing."""
        _, total_time = self.player.get_time()
        if total_time > 0:
            self.total_time = total_time
            events.media_loaded_total_time.emit(total_time)
            print(f"Total time set: {total_time}")
        else:
            # If still not available, try again
            QTimer.singleShot(500, self._get_total_time)

    def play(self):
        self.player.play()
        self.is_playing = True
        events.play_state_changed.emit(self.is_playing)

    def pause(self):
        self.player.pause()
        self.is_playing = False
        events.play_state_changed.emit(self.is_playing)

    def toggle_play(self, should_play: bool) -> None:
        """
        Change the play state of the player.
        """
        if should_play:
            self.play()
        else:
            self.pause()

    def toggle_play_pause(self):
        """Toggle the play state of the player."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def rewind(self, seconds: int = 10) -> None:
        self.player.rewind(seconds)
        self._update_position()

    def forward(self, seconds: int = 10) -> None:
        self.player.forward(seconds)
        self._update_position()

    def slow_down(self):
        rate = self.player.decrease_speed()
        events.rate_changed.emit(rate)
        return rate

    def seek(self, position_percent: float) -> None:
        """
        Move to a specific position.
        Args:
            position_percent (float) between 0 and 1
        """
        self.player.seek(position_percent)
        self._update_position()

    def _update_position(self):
        current_time, _ = self.player.get_time()
        events.position_changed.emit(current_time, self.total_time)

        # If we are at the end of the media
        if current_time >= self.total_time - 0.5 and self.total_time > 0:
            if self.loop_enabled:
                # Relaunch the playback from the beginning
                self.player.seek(0)
                self.play()
            else:
                # Stop the playback
                self.player.stop()
                self.is_playing = False
                events.play_state_changed.emit(self.is_playing)
                events.media_ended.emit()

    def set_video_output(self, win_id):
        """
        Configure la sortie vidéo pour le player.
        Cette méthode est spécifique à chaque implémentation de Player.
        """
        if hasattr(self.player, "set_video_output"):
            self.player.set_video_output(win_id)

    def cleanup(self):
        self.timer.stop()
        self.player.cleanup()

    def get_current_time(self):
        """Return the current position of the player."""
        current_time, _ = self.player.get_time()
        return current_time, self.total_time

    def get_total_time(self):
        """Return the total duration of the player."""
        return self.total_time

    def toggle_loop(self):
        """Toggle the loop state of the player."""
        self.loop_enabled = not self.loop_enabled
        return self.loop_enabled
