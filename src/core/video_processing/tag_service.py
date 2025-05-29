"""
Tag management module.
Contains classes and functions for managing tags in the application.
"""

import time
import os
import json
from typing import List, Tuple, Optional

from src.core.constants import tags_path
from src.core.event_handler import events
from src.core.logging_config import logger


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
        video_filename = os.path.basename(video_path)
        tags_file = os.path.join(tags_path, video_filename.replace(".mp4", ".json"))
        return tags_file

    def reload_tags(self) -> None:
        """Reload tags for the current video."""
        if self.current_video_path:
            logger.info(f"Reloading tags for video: {self.current_video_path}")
            self.load_tags_for_video(self.current_video_path)

    def load_tags_for_video(self, video_path: str) -> None:
        """
        Load tags for a specific video.
        """
        self.current_video_path = video_path
        tags_file = self._get_tags_file_path(video_path)
        logger.info(f"Loading tags for video: {tags_file}")

        if os.path.exists(tags_file):
            try:
                with open(tags_file, "r", encoding="utf-8") as f:
                    self._tags = json.load(f)
            except OSError as e:
                logger.error(f"Error loading tags: {e}")
                self._tags = []
        else:
            self._tags = []

        events.tags_updated.emit(self._sorted_tags())

    def save_tags(self) -> None:
        """
        Save current tags to JSON file.
        """
        if not self.current_video_path:
            logger.warning("No current video path, cannot save tags")
            return

        tags_file = self._get_tags_file_path(self.current_video_path)
        logger.info(f"Saving tags to file: {tags_file}")

        try:
            with open(tags_file, "w", encoding="utf-8") as f:
                json.dump(self._tags, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully saved {len(self._tags)} tags")
        except OSError as e:
            logger.error(f"Error saving tags to file: {e}")

    def _sorted_tags(self) -> List[Tuple[str, str, str]]:
        """Return a sorted copy of tags by timestamp."""
        return sorted(
            self._tags.copy(), key=lambda x: float(x[0])
        )  # x[0] is the timestamp

    def add_tag(self, tag_name: str, timestamp: float = None) -> Tuple[str, str, str]:
        """
        Add a tag to the list
        Args:
            tag_name: Name of the tag to add.
            timestamp: Tag timestamp. If None, uses current time.
        Returns:
            A tuple containing (timestamp, tag_name, display_time).
        """
        # Store timestamp in seconds and MM:SS format for display
        display_time = time.strftime("%M:%S", time.gmtime(timestamp))
        tag = (str(timestamp), tag_name, display_time)
        self._tags.append(tag)

        # Save tags to file
        self.save_tags()

        events.tags_updated.emit(self._sorted_tags())
        return tag

    def add_tag_at_time(self, timestamp: float) -> None:
        if not self.current_video_path:
            logger.warning("No video loaded, cannot add tag")
            return

        new_tag_name = f"Tag {len(self._tags) + 1}"
        self.add_tag(new_tag_name, timestamp)
        logger.info(f"Added tag '{new_tag_name}' at {timestamp}s")

    def get_tags(self) -> List[Tuple[str, str, str]]:
        return self._tags

    def clear_tags(self) -> None:
        self._tags = []
        events.tags_updated.emit(self._tags)

    def delete_tag(self, timestamp: str) -> None:
        self._tags = [tag for tag in self._tags if tag[0] != timestamp]
        self.save_tags()
        events.tags_updated.emit(self._tags)
