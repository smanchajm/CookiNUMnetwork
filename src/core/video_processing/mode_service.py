"""
Service for managing application modes (Live/Review).
Handles transitions between different modes and notifies concerned sections.
"""

from enum import Enum, auto
from typing import Callable, List

from src.core.event_handler import events
from src.core.logging_config import logger


class Mode(Enum):
    """Possible application states."""

    REVIEW = auto()
    LIVE = auto()


class ModeService:
    """
    Application mode manager.
    Implements a simple state machine to handle mode transitions.
    """

    def __init__(self):
        self._mode = Mode.LIVE
        self._transition_callbacks: List[Callable[[Mode, Mode], None]] = []

    def initialize(self) -> None:
        """
        Initialize the service and notify observers of the default mode.
        """
        # Notify observers of initial mode
        logger.info(f"ModeService initialized with live mode: {self.is_live_mode}")
        events.live_mode_changed.emit(self.is_live_mode)

    def set_mode(self, new_mode: Mode) -> None:
        """
        Change the application mode.

        Args:
            new_mode: The new mode to activate.
        """
        if new_mode == self._mode:
            return

        old_mode = self._mode
        self._mode = new_mode

        # Notify transition callbacks
        for callback in self._transition_callbacks:
            callback(old_mode, new_mode)

        # Emit global Signal
        events.live_mode_changed.emit(self.is_live_mode)

    def get_mode(self) -> Mode:
        """Return the current mode."""
        return self._mode

    @property
    def is_live_mode(self) -> bool:
        """Indicates if the application is in live mode."""
        return self._mode == Mode.LIVE

    def add_transition_callback(self, callback: Callable[[Mode, Mode], None]) -> None:
        """
        Add a callback that will be called when mode changes.

        Args:
            callback: Function called with (old_mode, new_mode).
        """
        self._transition_callbacks.append(callback)

    def toggle_live_mode(self) -> None:
        """Switch to live mode."""
        self.set_mode(Mode.LIVE)

    def toggle_review_mode(self) -> None:
        """Switch to review mode."""

        self.set_mode(Mode.REVIEW)
