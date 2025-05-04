from PyQt6.QtCore import QObject

from src.core.event_handler import events


class RecordingService(QObject):
    """
    Service gérant l'enregistrement vidéo.
    Centralise l'état d'enregistrement et notifie les composants concernés.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        """Indique si l'enregistrement est en cours."""
        return self._is_recording

    def start_recording(self) -> None:
        """
        Démarre l'enregistrement.
        """
        if not self._is_recording:
            self._is_recording = True
            events.recording_state_changed.emit(True)

    def stop_recording(self) -> None:
        """
        Arrête l'enregistrement.
        """
        if self._is_recording:
            self._is_recording = False
            events.recording_state_changed.emit(False)

    def toggle_recording(self) -> None:
        """
        Bascule l'état d'enregistrement.
        """
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()
