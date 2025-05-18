import queue
import threading
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.event_handler import events
from src.core.constants import audio_model_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.core.voice_recognition.canonical_phrases import (
    CANONICAL_PHRASES,
    INTENT_TO_COMMAND,
)


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

        # Initialize Vosk model
        self.model = None
        self.recognizer = None
        self._initialize_model()

        # Initialize TF-IDF vectorizer for semantic matching
        print("Initializing TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            min_df=1,  # Minimum document frequency
            max_df=1.0,  # Maximum document frequency
            strip_accents="unicode",
            lowercase=True,
        )

        # Prepare all phrases for vectorization
        self.all_phrases = []
        self.phrase_to_intent = {}
        for intent, phrases in CANONICAL_PHRASES.items():
            for phrase in phrases:
                self.all_phrases.append(phrase)
                self.phrase_to_intent[phrase] = intent

        # Fit the vectorizer and transform all phrases
        self.phrase_vectors = self.vectorizer.fit_transform(self.all_phrases)
        print("TF-IDF vectorizer initialized")

        # Command mapping
        self.commands = {
            "play": lambda: events.play_pause_signal.emit(),
            "jouer": lambda: events.play_pause_signal.emit(),
            "pause": lambda: events.play_pause_signal.emit(),
            "avancer": lambda: events.forward_signal.emit(),
            "reculer": lambda: events.rewind_signal.emit(),
            "ajouter un tag": lambda: events.add_tag_clicked.emit(),
            "démarrer enregistrement": lambda: events.start_recording_clicked.emit(),
            "arrêter enregistrement": lambda: events.start_recording_clicked.emit(),
            "mode direct": lambda: events.live_mode_clicked.emit(),
            "mode révision": lambda: events.review_mode_clicked.emit(),
            "ouvrir": lambda: events.open_video_clicked.emit(),
        }

    def _initialize_model(self):
        """Initialize the Vosk model with proper path handling."""
        try:
            print(f"Loading Vosk model from: {audio_model_path}")
            self.model = Model(audio_model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            print("Vosk model loaded successfully")
        except Exception as e:
            print(f"Error loading Vosk model: {e}")
            self.model = None
            self.recognizer = None

    def start(self):
        """Start the voice recognition service."""
        if self.is_running or not self.model:
            if not self.model:
                print("Cannot start voice recognition: No model loaded")
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
        print("Stopping voice recognition service...")
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
            print(f"Error stopping audio stream: {e}")

        # Join threads with timeout
        if self.thread:
            self.thread.join(timeout=1.0)
            if self.thread.is_alive():
                print("Warning: Audio processing thread did not terminate gracefully")
            self.thread = None

        if self.audio_thread:
            self.audio_thread.join(timeout=2.0)
            if self.audio_thread.is_alive():
                print("Warning: Audio recording thread did not terminate gracefully")
            self.audio_thread = None

        print("Voice recognition service stopped")

    def _start_audio_recording(self):
        """Start recording audio in a separate thread."""

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            self.audio_queue.put(bytes(indata))

        try:
            print("Initializing audio stream...")
            with sd.InputStream(
                samplerate=16000, channels=1, dtype=np.int16, callback=audio_callback
            ):
                print("Audio stream initialized successfully")
                while self.is_running:
                    sd.sleep(100)
        except Exception as e:
            print(f"Error in audio recording: {e}")

    def _process_audio(self):
        """Process audio data and recognize commands."""
        print("Starting audio processing...")
        while self.is_running:
            try:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if result.get("text"):
                        text = result["text"].lower()
                        print(f"Recognized text: {text}")
                        self._handle_command(text)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")

    def _get_semantic_intent(self, text: str) -> str:
        """
        Get the semantic intent from the input text using TF-IDF and cosine similarity.

        Args:
            text: The input text to analyze

        Returns:
            The matched intent if similarity > 0.6, None otherwise
        """
        # Transform the input text
        text_vector = self.vectorizer.transform([text])

        # Calculate similarities with all phrases
        similarities = cosine_similarity(text_vector, self.phrase_vectors)[0]

        # Find the best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        if best_similarity > 0.6:  # Minimum threshold
            best_phrase = self.all_phrases[best_idx]
            best_intent = self.phrase_to_intent[best_phrase]
            print(
                f"Matched '{text}' to intent '{best_intent}' with similarity {best_similarity:.2f}"
            )
            print(f"Best matching phrase: '{best_phrase}'")
            return best_intent

        return None

    def _handle_command(self, text):
        """Handle recognized voice commands."""
        # First try exact matching
        for command, action in self.commands.items():
            if command in text:
                print(f"Executing exact match command: {command}")
                action()
                return

        # If no exact match, try semantic matching
        intent = self._get_semantic_intent(text)
        if intent:
            command = INTENT_TO_COMMAND.get(intent)
            if command and command in self.commands:
                print(f"Executing semantic match command: {command}")
                self.commands[command]()
                return

        print(f"No matching command found for: {text}")
