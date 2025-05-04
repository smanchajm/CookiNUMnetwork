from PyQt6.QtCore import QObject


class RecordingService(QObject):
    """
    Service gérant l'enregistrement vidéo.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def start_recording(self):
        """
        Démarre l'enregistrement.
        """
        pass

    def stop_recording(self):
        """
        Arrête l'enregistrement.
        """
        pass
