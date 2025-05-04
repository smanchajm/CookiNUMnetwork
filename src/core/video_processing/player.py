from abc import ABC, abstractmethod
import sys
import vlc
import cv2
import time
import threading
from typing import Optional, Tuple
import ctypes


class Player(ABC):
    """
    Interface abstraite pour un lecteur multimédia.
    Définit les méthodes essentielles que tout lecteur doit implémenter.
    """

    @abstractmethod
    def load(self, media_path):
        """
        Charge un fichier média dans le lecteur.

        Args:
            media_path (str): Chemin vers le fichier média.

        Returns:
            bool: True si le chargement a réussi, False sinon.
        """
        pass

    @abstractmethod
    def play(self):
        """Démarre la lecture."""
        pass

    @abstractmethod
    def pause(self):
        """Met en pause la lecture."""
        pass

    @abstractmethod
    def stop(self):
        """Arrête la lecture."""
        pass

    @abstractmethod
    def rewind(self, seconds=10):
        """
        Recule la lecture de X secondes.

        Args:
            seconds (int): Nombre de secondes à reculer (défaut: 10).
        """
        pass

    @abstractmethod
    def forward(self, seconds=10):
        """
        Avance la lecture de X secondes.

        Args:
            seconds (int): Nombre de secondes à avancer (défaut: 10).
        """
        pass

    @abstractmethod
    def set_speed(self, speed):
        """
        Définit la vitesse de lecture.

        Args:
            speed (float): Vitesse de lecture.

        Returns:
            float: La vitesse de lecture appliquée.
        """
        pass

    @abstractmethod
    def decrease_speed(self):
        """
        Réduit la vitesse de lecture d'un niveau.

        Returns:
            float: La nouvelle vitesse de lecture.
        """
        pass

    @abstractmethod
    def seek(self, position):
        """
        Déplace la lecture à une position spécifique.

        Args:
            position (float): Position en pourcentage (0.0 à 1.0).
        """
        pass

    @abstractmethod
    def get_time(self):
        """
        Retourne la position actuelle et la durée totale.

        Returns:
            tuple: (position_actuelle, durée_totale) en secondes.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Libère les ressources du lecteur."""
        pass

    def set_video_output(self, win_id):
        """
        Configure la sortie vidéo pour le lecteur.
        Cette méthode est optionnelle et peut être implémentée par les classes filles.

        Args:
            win_id: Identifiant de la fenêtre pour l'affichage vidéo.
        """
        pass


class VLCPlayer(Player):
    """
    Implémentation concrète d'un lecteur utilisant VLC.
    """

    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.playback_speed = 1.0  # Vitesse de lecture normale
        self.speed_levels = [0.25, 0.5, 0.75, 1.0]  # Niveaux de vitesse disponibles

    def load(self, media_path):
        """
        Charge un fichier média dans le lecteur.

        Args:
            media_path (str): Chemin vers le fichier média.

        Returns:
            bool: True si le chargement a réussi, False sinon.
        """
        try:
            media = self.vlc_instance.media_new(media_path)
            self.media_player.set_media(media)
            return True
        except Exception:
            return False

    def play(self):
        """Démarre la lecture."""
        self.media_player.play()

    def pause(self):
        """Met en pause la lecture."""
        self.media_player.pause()

    def stop(self):
        """Arrête la lecture."""
        self.media_player.stop()

    def rewind(self, seconds=10):
        """
        Recule la lecture de X secondes.

        Args:
            seconds (int): Nombre de secondes à reculer (défaut: 10).
        """
        current_time = self.media_player.get_time() / 1000.0
        new_time = max(0, current_time - seconds) * 1000
        self.media_player.set_time(int(new_time))

    def forward(self, seconds=10):
        """
        Avance la lecture de X secondes.

        Args:
            seconds (int): Nombre de secondes à avancer (défaut: 10).
        """
        current_time = self.media_player.get_time() / 1000.0
        total_time = self.media_player.get_length() / 1000.0
        new_time = min(total_time, current_time + seconds) * 1000
        self.media_player.set_time(int(new_time))

    def set_speed(self, speed):
        """
        Définit la vitesse de lecture.

        Args:
            speed (float): Vitesse de lecture (0.25 à 1.0).

        Returns:
            float: La vitesse de lecture appliquée.
        """
        if speed in self.speed_levels:
            self.playback_speed = speed
            self.media_player.set_rate(speed)
        return self.playback_speed

    def decrease_speed(self):
        """
        Réduit la vitesse de lecture d'un niveau.
        Revient à la vitesse normale si on est déjà au minimum.

        Returns:
            float: La nouvelle vitesse de lecture.
        """
        try:
            current_index = self.speed_levels.index(self.playback_speed)
        except ValueError:
            current_index = self.speed_levels.index(1.0)

        next_index = (current_index - 1) % len(self.speed_levels)
        return self.set_speed(self.speed_levels[next_index])

    def seek(self, position):
        """
        Déplace la lecture à une position spécifique.

        Args:
            position (float): Position en pourcentage (0.0 à 1.0).
        """
        self.media_player.set_position(position)

    def get_time(self):
        """
        Retourne la position actuelle et la durée totale.

        Returns:
            tuple: (position_actuelle, durée_totale) en secondes.
        """
        current_time = self.media_player.get_time() / 1000.0
        total_time = self.media_player.get_length() / 1000.0
        return current_time, total_time

    def cleanup(self):
        """Libère les ressources du lecteur."""
        self.media_player.stop()
        self.media_player.release()
        self.vlc_instance.release()

    def set_video_output(self, win_id):
        """Configure la sortie vidéo pour VLC."""
        if sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(win_id))
        elif sys.platform == "win32":
            # Utiliser directement le handle de la fenêtre
            self.media_player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(win_id))


class OpenCVPlayer(Player):
    """
    Implémentation d'un lecteur utilisant OpenCV.
    Permet la lecture de vidéos avec des fonctionnalités de traitement d'image.
    """

    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_frame = None
        self.is_playing = False
        self.is_paused = False
        self.playback_speed = 1.0
        self.speed_levels = [0.25, 0.5, 0.75, 1.0]
        self.frame_delay = 0  # Délai entre les frames en ms
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
        """Met à jour le délai entre les frames en fonction de la vitesse de lecture."""
        if self.cap is not None:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                self.frame_delay = int(1000 / (fps * self.playback_speed))

    def _play_loop(self):
        """Boucle de lecture principale."""
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
                time.sleep(0.1)  # Évite une boucle trop intensive en pause

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
        """
        Configure la sortie vidéo pour OpenCV.
        Note: OpenCV utilise sa propre fenêtre, donc win_id n'est pas utilisé.
        """
        pass  # OpenCV gère sa propre fenêtre
