"""
Service de gestion des modes de l'application (Live/Review).
Gère les transitions entre les différents modes et notifie les composants concernés.
"""

from enum import Enum, auto
from typing import Callable, List

from src.core.event_handler import events


class Mode(Enum):
    """États possibles de l'application."""

    REVIEW = auto()
    LIVE = auto()


class ModeService:
    """
    Gestionnaire des modes de l'application.
    Implémente une machine à états simple pour gérer les transitions entre modes.
    """

    def __init__(self):
        self._mode = Mode.REVIEW
        self._transition_callbacks: List[Callable[[Mode, Mode], None]] = []

    def set_mode(self, new_mode: Mode) -> None:
        """
        Change le mode de l'application.

        Args:
            new_mode: Le nouveau mode à activer.
        """
        if new_mode == self._mode:
            return

        old_mode = self._mode
        self._mode = new_mode

        # Notifier les callbacks de transition
        for callback in self._transition_callbacks:
            callback(old_mode, new_mode)

        # Émettre le signal global
        events.live_mode_changed.emit(self.is_live_mode)

    def get_mode(self) -> Mode:
        """Retourne le mode actuel."""
        return self._mode

    @property
    def is_live_mode(self) -> bool:
        """Indique si l'application est en mode live."""
        return self._mode == Mode.LIVE

    def add_transition_callback(self, callback: Callable[[Mode, Mode], None]) -> None:
        """
        Ajoute un callback qui sera appelé lors d'un changement de mode.

        Args:
            callback: Fonction appelée avec (ancien_mode, nouveau_mode).
        """
        self._transition_callbacks.append(callback)

    def toggle_live_mode(self) -> None:
        """Bascule vers le mode live."""
        self.set_mode(Mode.LIVE)

    def toggle_review_mode(self) -> None:
        """Bascule vers le mode review."""
        self.set_mode(Mode.REVIEW)
