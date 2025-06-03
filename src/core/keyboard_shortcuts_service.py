from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget

from src.core.event_handler import events


class KeyboardShortcutsService:
    """
    Manages the application's keyboard shortcuts.
    Uses PyQt6's QShortcut for native shortcut handling.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.shortcuts = {}
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Configure all application keyboard shortcuts."""
        # Playback shortcuts
        self._add_shortcut("Space", events.play_pause_signal.emit)
        self._add_shortcut("Right", events.forward_signal.emit)
        self._add_shortcut("Left", events.rewind_signal.emit)

        # Mode shortcuts
        self._add_shortcut("D", events.live_mode_clicked.emit)
        self._add_shortcut("R", events.review_mode_clicked.emit)

        # Recording shortcuts
        self._add_shortcut("E", events.start_recording_clicked.emit)

        # Tag shortcuts
        self._add_shortcut("T", events.add_tag_clicked.emit)

        # File shortcuts
        self._add_shortcut("Ctrl+O", events.open_video_clicked.emit)

    def _add_shortcut(self, key_sequence: str, callback, *args):
        """
        Add a new keyboard shortcut.

        Args:
            key_sequence: The key sequence (e.g., "Ctrl+S")
            callback: The function to call
            *args: Additional arguments to pass to the function
        """
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
        shortcut.activated.connect(lambda: callback(*args))
        self.shortcuts[key_sequence] = shortcut

    def remove_shortcut(self, key_sequence: str):
        """
        Remove a keyboard shortcut.

        Args:
            key_sequence: The key sequence to remove
        """
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence].deleteLater()
            del self.shortcuts[key_sequence]
