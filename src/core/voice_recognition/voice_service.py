import json
import queue
import threading
import sys
import locale
import os

import numpy as np
import sounddevice as sd
from num2words import num2words
from PySide6.QtCore import QObject
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vosk import Model, KaldiRecognizer

from src.core.event_handler import events
from src.core.logging_config import logger
from src.core.voice_recognition.canonical_phrases import (
    CANONICAL_PHRASES,
    INTENT_TO_COMMAND,
    TRIGGER_PHRASES,
    IMPORTANT_WORDS,
)
from src.utils.resource_manager import ResourceManager


class CommandMatcher:
    def __init__(self, min_similarity=0.4):
        self.commands = {}
        self.command_texts = []
        self.command_mapping = {}
        self.min_similarity = min_similarity
        self.vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2))

    def add_command(self, command_id, action, main_phrase=None, variants=None):
        self.commands[command_id] = action
        if main_phrase:
            self.command_texts.append(main_phrase)
            self.command_mapping[main_phrase] = command_id
        if variants:
            for variant in variants:
                if variant:
                    self.command_texts.append(variant)
                    self.command_mapping[variant] = command_id

    def match_command(self, text):
        if not self.command_texts:
            return None, 0.0, None

        # Check exact match
        if text in self.command_mapping:
            command_id = self.command_mapping[text]
            return command_id, 1.0, self.commands[command_id]

        # Check partial match
        best_match = None
        best_score = 0.0
        for cmd_text, cmd_id in self.command_mapping.items():
            cmd_words = set(cmd_text.split())
            input_words = set(text.split())
            matching_words = cmd_words.intersection(input_words)
            if matching_words:
                score = sum(
                    len(word) for word in matching_words if len(word) > 3
                ) / len(cmd_words)
                if any(word in IMPORTANT_WORDS for word in matching_words):
                    score *= 1.5
                if score > best_score:
                    best_score = score
                    best_match = (cmd_id, score)

        if best_match and best_score >= 0.6:
            cmd_id, score = best_match
            return cmd_id, score, self.commands[cmd_id]

        # Use TF-IDF + cosine similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform(self.command_texts + [text])
            similarities = cosine_similarity(
                tfidf_matrix[-1], tfidf_matrix[:-1]
            ).flatten()
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]

            if best_similarity >= self.min_similarity:
                best_command_text = self.command_texts[best_idx]
                command_id = self.command_mapping[best_command_text]
                return command_id, best_similarity, self.commands[command_id]
        except Exception as e:
            logger.error(f"Error in command matching: {e}")

        return None, 0.0, None


class VoiceService(QObject):
    """
    Service for voice command recognition using Vosk.
    Runs in a background thread to avoid blocking the UI.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        self.audio_thread = None
        self.model = None
        self.recognizer = None
        self.command_matcher = CommandMatcher()

        # Lo de la configuration d'encodage
        logger.info(f"Python default encoding: {sys.getdefaultencoding()}")
        logger.info(f"System locale: {locale.getlocale()}")

        self._initialize_models()
        self._initialize_commands()

    def _initialize_models(self):
        """Initialize French Vosk model with proper path handling."""
        try:
            self.model = Model(str(ResourceManager.get_audio_model_path()))
            self.recognizer = KaldiRecognizer(self.model, 16000)
            logger.info("French Vosk model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Vosk model: {e}")
            self.model = None
            self.recognizer = None

    def _initialize_commands(self):
        """Initialize commands with their variants using canonical phrases."""
        # Command mapping with actions
        command_actions = {
            "play": lambda: events.play_pause_Signal.emit(),
            "pause": lambda: events.play_pause_Signal.emit(),
            "forward": lambda: events.forward_Signal.emit(),
            "backward": lambda: events.rewind_Signal.emit(),
            "tag": lambda: events.add_tag_clicked.emit(),
            "record": lambda: events.start_recording_clicked.emit(),
            "stop_record": lambda: events.start_recording_clicked.emit(),
            "live": lambda: events.live_mode_clicked.emit(),
            "review": lambda: events.review_mode_clicked.emit(),
            "open": lambda: events.open_video_clicked.emit(),
            "open_last_video": lambda: events.load_last_video_clicked.emit(),
            "goto_tag": lambda text: self._handle_goto_tag(text),
            "zoom": lambda: events.cycle_zoom_Signal.emit(),
            "zoom_in": lambda: events.zoom_in_Signal.emit(),
            "zoom_out": lambda: events.zoom_out_Signal.emit(),
            "slow_down": lambda: events.slow_down_Signal.emit(),
        }

        # Add commands using canonical phrases
        for intent, phrases in CANONICAL_PHRASES.items():
            if intent in command_actions:
                # Get the main command text from INTENT_TO_COMMAND
                main_phrase = INTENT_TO_COMMAND.get(intent, intent)
                # Add the command with all its variants
                self.command_matcher.add_command(
                    command_id=intent,
                    action=command_actions[intent],
                    main_phrase=main_phrase,
                    variants=phrases,
                )

    def _extract_tag_number(self, text: str) -> int | None:
        """Extract a number (1 to 30) from digits or French words in text."""
        text = text.lower()
        # Mapping of variants of the number in french
        number_variants = {
            2: [
                "de",
            ],
        }
        for i in range(1, 31):
            variants = [
                num2words(i, lang="fr"),
                num2words(i, lang="fr").replace("-", " "),
            ]
            for v in variants:
                if v in text:
                    return i

        # If no number is found, check the variants of the number
        for num, variants in number_variants.items():
            for variant in variants:
                if variant in text:
                    return num
        return None

    def _handle_command(self, text):
        """Handle recognized voice commands."""
        text_lower = text.lower()
        if not any(trigger in text_lower for trigger in TRIGGER_PHRASES):
            return

        # Try to match the command
        best_command, similarity, action = self.command_matcher.match_command(text)
        logger.info(
            f"{'Command recognized: ' + best_command if best_command else 'No matching command found for: ' + text} (score: {similarity:.2f})"
        )

        # Execute action if command found
        if best_command:
            events.voice_command_recognized.emit()
            if best_command == "goto_tag":
                self._handle_goto_tag(text)
            else:
                action()

    def _handle_goto_tag(self, text: str):
        """Handle goto tag command."""
        tag_number = self._extract_tag_number(text)
        if tag_number is not None:
            logger.info(f"Navigating to tag number: {tag_number}")
            events.request_tag_timestamp.emit(tag_number)

    def start(self):
        """Start the voice recognition service."""
        if self.is_running or not self.model:
            if not self.model:
                logger.error("Cannot start voice recognition: Model not loaded")
            return

        self.is_running = True
        # Start audio recording thread
        self.audio_thread = threading.Thread(target=self._start_audio_recording)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Start processing thread
        self.thread = threading.Thread(target=self._process_audio)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the voice recognition service."""
        logger.info("Stopping voice recognition service...")
        self.is_running = False

        # Clear the audio queue to prevent blocking
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Stop audio stream if it exists
        try:
            sd.stop()
        except Exception as e:
            logger.error(f"Error stopping audio stream: {e}")

        # Join threads with timeout and force stop if necessary
        if self.thread:
            try:
                self.thread.join(timeout=2.0)
                if self.thread.is_alive():
                    logger.warning(
                        "Audio processing thread did not terminate gracefully, forcing stop"
                    )
                    # Force stop by setting is_running to False again
                    self.is_running = False
                    self.thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error stopping audio processing thread: {e}")
            finally:
                self.thread = None

        if self.audio_thread:
            try:
                self.audio_thread.join(timeout=2.0)
                if self.audio_thread.is_alive():
                    logger.warning(
                        "Audio recording thread did not terminate gracefully, forcing stop"
                    )
                    # Force stop by setting is_running to False again
                    self.is_running = False
                    self.audio_thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error stopping audio recording thread: {e}")
            finally:
                self.audio_thread = None

        logger.info("Voice recognition service stopped")

    def cleanup(self):
        """Clean up resources before application exit."""
        self.stop()
        # Additional cleanup if needed
        if self.model:
            self.model = None
        if self.recognizer:
            self.recognizer = None

    def _start_audio_recording(self):
        """Start recording audio in a separate thread."""

        def audio_callback(indata, frames, time, status):
            self.audio_queue.put(bytes(indata))

        try:
            logger.info("Initializing audio stream...")
            with sd.InputStream(
                samplerate=16000, channels=1, dtype=np.int16, callback=audio_callback
            ):
                logger.info("Audio stream initialized successfully")
                while self.is_running:
                    sd.sleep(100)
        except Exception as e:
            logger.error(f"Error in audio recording: {e}")

    def _process_audio(self):
        """Process audio data and recognize commands."""
        logger.info("Starting audio processing...")
        while self.is_running:
            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                if result.get("text"):
                    # Forcer l'encodage UTF-8 pour le texte reconnu
                    raw_text = (
                        result["text"].encode("utf-8", errors="replace").decode("utf-8")
                    )
                    logger.debug(
                        f"Raw Vosk output (encoded): {raw_text.encode('utf-8')}"
                    )
                    text = raw_text.lower()
                    logger.info(f"Recognized text: {text}")
                    self._handle_command(text)
