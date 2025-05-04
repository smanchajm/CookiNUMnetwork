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

        # Timer pour mettre à jour la position
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._update_position)
        self.timer.start()

        events.media_loaded.connect(self.load_media)

    def open_video_file(self, parent_widget=None, start_dir=video_files_path):
        """
        Ouvre une boîte de dialogue pour sélectionner un fichier vidéo.

        Args:
            parent_widget: Widget parent pour la boîte de dialogue
            start_dir: Dossier de départ pour le file explorer (par défaut: dossier personnel)

        Returns:
            str: Chemin du fichier sélectionné ou None si l'utilisateur a annulé
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
            self.play()
            return True
        else:
            self.pause()
            events.media_error.emit(f"Impossible de charger le fichier: {path}")
            return False

    def play(self):
        self.player.play()
        self.is_playing = True
        events.play_state_changed.emit(self.is_playing)

    def pause(self):
        self.player.pause()
        self.is_playing = False
        events.play_state_changed.emit(self.is_playing)

    def toggle_play(self, should_play):
        """
        Change l'état de lecture du lecteur.

        Args:
            should_play (bool): True pour lancer la lecture, False pour mettre en pause
        """
        if should_play:
            self.play()
        else:
            self.pause()

    def rewind(self, seconds=10):
        """
        Recule de quelques secondes dans la lecture.

        Args:
            seconds (int): Nombre de secondes à reculer.
        """
        self.player.rewind(seconds)
        self._update_position()

    def forward(self, seconds=10):
        self.player.forward(seconds)
        self._update_position()

    def slow_down(self):
        rate = self.player.decrease_speed()
        events.rate_changed.emit(rate)
        return rate

    def seek(self, position_percent):
        """
        Déplace la lecture à une position spécifique.

        Args:
            position_percent (float): Position en pourcentage (0-1)
        """
        self.player.seek(position_percent)
        self._update_position()

    def _update_position(self):
        """
        Met à jour la position actuelle et émet un signal.
        """
        current_time, total_time = self.player.get_time()
        events.position_changed.emit(current_time, total_time)

        # Si on est à la fin du média, revenir au début
        if current_time >= total_time - 0.5 and total_time > 0:
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
