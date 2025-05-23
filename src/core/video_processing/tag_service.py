"""
Tag management module.
Contains classes and functions for managing tags in the application.
"""

import time
import os
import json
from typing import List, Tuple, Optional

from src.core.event_handler import events
from src.core.constants import tags_path


class TagService:
    """
    Tag manager that encapsulates tag management logic.
    """

    def __init__(self):
        self._tags: List[Tuple[str, str, str]] = []
        self.current_video_path: Optional[str] = None

        # Create tags directory if it doesn't exist
        if not os.path.exists(tags_path):
            os.makedirs(tags_path)

    def _get_tags_file_path(self, video_path: str) -> str:
        """Get the path to the JSON file storing tags for a video."""
        # Get the video filename and replace .mp4 with .json
        video_filename = os.path.basename(video_path)
        tags_filename = video_filename.replace(".mp4", ".json")
        tags_file = os.path.join(tags_path, tags_filename)
        print(f"Tags file path: {tags_file}")
        return tags_file

    def reload_tags(self) -> None:
        """Reload tags for the current video."""
        if self.current_video_path:
            print("Reloading tags for video:", self.current_video_path)
            self.load_tags_for_video(self.current_video_path)

    def load_tags_for_video(self, video_path: str) -> None:
        """
        Load tags for a specific video.

        Args:
            video_path: Path to the video file.
        """
        self.current_video_path = video_path
        tags_file = self._get_tags_file_path(video_path)
        print(f"Loading tags for video: {tags_file}")

        if os.path.exists(tags_file):
            try:
                with open(tags_file, "r", encoding="utf-8") as f:
                    self._tags = json.load(f)
                # Sort tags after loading
                self._sort_tags()
                events.tags_updated.emit(self._tags)
            except Exception as e:
                print(f"Error loading tags: {str(e)}")
                self._tags = []
        else:
            self._tags = []
            events.tags_updated.emit(self._tags)

    def save_tags(self) -> None:
        """
        Save current tags to JSON file.
        """
        if not self.current_video_path:
            print("No current video path, cannot save tags")
            return

        tags_file = self._get_tags_file_path(self.current_video_path)
        print(f"Saving tags to file: {tags_file}")
        try:
            # Create the tags file if it doesn't exist
            with open(tags_file, "w", encoding="utf-8") as f:
                json.dump(self._tags, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(self._tags)} tags")
        except Exception as e:
            print(f"Error saving tags: {str(e)}")

    def _sort_tags(self) -> None:
        """Sort tags by timestamp."""
        self._tags.sort(key=lambda x: float(x[0]))  # x[0] is the timestamp string

    def add_tag(self, tag_name: str, timestamp: float = None) -> Tuple[str, str, str]:
        """
        Add a tag to the list
        Args:
            tag_name: Name of the tag to add.
            timestamp: Tag timestamp. If None, uses current time.
        Returns:
            A tuple containing (timestamp, tag_name, display_time).
        """
        # Stocker le timestamp en secondes et le format MM:SS pour l'affichage
        display_time = time.strftime("%M:%S", time.gmtime(timestamp))
        tag = (str(timestamp), tag_name, display_time)
        self._tags.append(tag)

        # Sort tags by timestamp
        self._sort_tags()

        # Save tags to file
        self.save_tags()

        events.tags_updated.emit(self._tags)
        return tag

    def add_tag_at_time(self, timestamp: float) -> None:
        if not self.current_video_path:
            print("No video loaded, cannot add tag")
            return

        new_tag_name = f"Tag {len(self._tags) + 1}"
        self.add_tag(new_tag_name, timestamp)
        print(f"Added tag '{new_tag_name}' at {timestamp}s")

    def get_tags(self) -> List[Tuple[str, str, str]]:
        """
        Retourne la liste des tags.
        """
        return self._tags.copy()

    def clear_tags(self) -> None:

        self._tags = []
        events.tags_updated.emit(self._tags)

    def clear_and_save_tags(self) -> None:
        """
        Réinitialise la liste des tags et sauvegarde le fichier vide
        """
        self._tags = []
        self.save_tags()
        events.tags_updated.emit(self._tags)

    def delete_tag(self, timestamp: str) -> None:
        self._tags = [tag for tag in self._tags if tag[0] != timestamp]
        self.save_tags()
        events.tags_updated.emit(self._tags)
