from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget
from src.core.event_handler import events


class KeyboardShortcutsService:
    """
    Gère les raccourcis clavier de l'application.
    Utilise QShortcut de PyQt6 pour une gestion native des raccourcis.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.shortcuts = {}
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Configure tous les raccourcis clavier de l'application."""
        # Raccourcis de lecture
        self._add_shortcut("Space", events.play_pause_signal.emit)
        self._add_shortcut("Right", events.forward_signal.emit)
        self._add_shortcut("Left", events.rewind_signal.emit)

        # Raccourcis de mode
        self._add_shortcut("D", events.live_mode_clicked.emit)
        self._add_shortcut("R", events.review_mode_clicked.emit)

        # Raccourcis d'enregistrement
        self._add_shortcut("E", events.start_recording_clicked.emit)

        # Raccourcis de tags
        self._add_shortcut("T", events.add_tag_clicked.emit)

        # Raccourcis de fichiers
        self._add_shortcut("Ctrl+O", events.open_video_clicked.emit)

    def _add_shortcut(self, key_sequence: str, callback, *args):
        """
        Ajoute un nouveau raccourci clavier.

        Args:
            key_sequence: La séquence de touches (ex: "Ctrl+S")
            callback: La fonction à appeler
            *args: Arguments additionnels à passer à la fonction
        """
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
        shortcut.activated.connect(lambda: callback(*args))
        self.shortcuts[key_sequence] = shortcut

    def remove_shortcut(self, key_sequence: str):
        """
        Supprime un raccourci clavier.

        Args:
            key_sequence: La séquence de touches à supprimer
        """
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence].deleteLater()
            del self.shortcuts[key_sequence]
