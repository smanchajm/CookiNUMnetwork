"""
Tag management module.
Contains classes and functions for managing tags in the application.
"""

import time
from typing import List, Tuple

from src.core.event_handler import events


class TagService:
    """
    Tag manager that encapsulates tag management logic.
    """

    def __init__(self):
        self._tags: List[Tuple[str, str, str]] = []

    def add_tag(self, tag_name: str, timestamp: float = None) -> Tuple[str, str, str]:
        """
        Add a tag to the list

        Args:
            tag_name: Name of the tag to add.
            timestamp: Tag timestamp. If None, uses current time.

        Returns:
            A tuple containing (timestamp, tag_name, display_time).
        """
        if timestamp is None:
            tag_time = time.time()
        else:
            tag_time = timestamp

        # Stocker le timestamp en secondes et le format MM:SS pour l'affichage
        display_time = time.strftime("%M:%S", time.gmtime(tag_time))
        tag = (str(tag_time), tag_name, display_time)
        self._tags.append(tag)

        events.tags_updated.emit(self._tags)

    def create_and_add_tag(self, timestamp: float) -> None:
        """
        Crée et ajoute un nouveau tag à la position spécifiée.
        """
        new_tag_name = f"Tag {len(self._tags) + 1}"
        self.add_tag(new_tag_name, timestamp)

    def get_tags(self) -> List[Tuple[str, str, str]]:
        """
        Retourne la liste des tags.
        """
        return self._tags.copy()

    def set_tags(self, tags: List[Tuple[str, str, str]]) -> None:
        """
        Met à jour la liste des tags

        Args:
            tags: La nouvelle liste de tags.
        """
        self._tags = tags.copy()
        events.tags_updated.emit(self._tags)

    def clear_tags(self) -> None:
        """
        Réinitialise la liste des tags
        """
        self._tags = []
        events.tags_updated.emit(self._tags)
