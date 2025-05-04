import time

from PyQt6.QtWidgets import QWidget, QLabel, QSlider, QStyle, QStyleOptionSlider
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap

from src.ui.widgets.action_button import ActionButton
from src.ui.utils.layouts import create_vbox_layout, create_hbox_layout
from src.ui.utils.qt_helpers import clear_layout, set_margins
from src.core.event_handler import events


class ProgressSlider(QSlider):
    """Slider personnalisé avec support pour les marqueurs de tags."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tag_positions = []
        # Charger l'icône SVG
        self.tag_icon = QIcon("src/ui/assets/icons/tag.svg")
        self.tag_icon_size = 20
        # Créer un pixmap à partir de l'icône
        self.tag_pixmap = self.tag_icon.pixmap(self.tag_icon_size, self.tag_icon_size)

    def add_tag_marker(self, position_percent):
        """Ajoute un marqueur de tag à la position spécifiée (0-1)."""
        if position_percent >= 0 and position_percent <= 1:
            self.tag_positions.append(position_percent)
            self.update()

    def clear_tag_markers(self):
        """Supprime tous les marqueurs de tags."""
        self.tag_positions.clear()
        self.update()

    def paintEvent(self, event):
        """
        Dessine le slider avec les marqueurs de tags.
        Called on update and init.
        """
        super().paintEvent(event)

        if not self.tag_positions:
            return

        # Obtenir les dimensions du slider
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            opt,
            QStyle.SubControl.SC_SliderGroove,
            self,
        )

        painter = QPainter(self)

        # Définir la taille du marqueur
        half_marker = self.tag_icon_size // 2
        for position in self.tag_positions:
            x = groove_rect.x() + int(position * groove_rect.width())
            y = groove_rect.y() + self.tag_icon_size
            painter.save()
            painter.translate(x, y)
            painter.rotate(-90)
            painter.drawPixmap(-half_marker, -half_marker, self.tag_pixmap)
            painter.restore()


class MediaControls(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("media_controls")
        self.is_playing = False
        self.is_programmatic_update = False
        self.setup_ui()

    def setup_ui(self):
        # Créer les boutons de contrôle
        self.rewind_btn = ActionButton(
            icon_path="src/ui/assets/icons/skip_previous.svg",
        )
        self.play_pause_btn = ActionButton(
            icon_path="src/ui/assets/icons/play_arrow.svg",
        )
        self.forward_btn = ActionButton(
            icon_path="src/ui/assets/icons/skip_next.svg",
        )
        self.slow_down_btn = ActionButton(
            icon_path="src/ui/assets/icons/slow_motion_video.svg",
        )

        self.timeline_label = QLabel("00:00/00:00")

        # Créer le slider de progression personnalisé
        self.progress_slider = ProgressSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)

        controls_layout = create_hbox_layout(
            widgets=[
                self.slow_down_btn,
                self.rewind_btn,
                self.play_pause_btn,
                self.forward_btn,
                self.timeline_label,
            ],
            spacing=5,
            margins=(10, 5, 10, 5),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        main_layout = create_vbox_layout(
            widgets=[controls_layout, self.progress_slider],
            spacing=5,
            margins=(10, 5, 10, 5),
        )

        self.setLayout(main_layout)
        self._connect_signals()

    def _connect_signals(self):
        self.slow_down_btn.clicked.connect(events.slow_down_signal.emit)
        self.rewind_btn.clicked.connect(events.rewind_signal.emit)
        self.play_pause_btn.clicked.connect(self.toggle_play)
        self.forward_btn.clicked.connect(events.forward_signal.emit)
        self.progress_slider.valueChanged.connect(self.on_slider_value_changed)

    def toggle_play(self):
        """
        Bascule l'état de lecture et met à jour l'interface
        """
        self.is_playing = not self.is_playing

        # Met à jour l'icône
        if self.is_playing:
            self.play_pause_btn._setup_icon("src/ui/assets/icons/pause.svg")
        else:
            self.play_pause_btn._setup_icon("src/ui/assets/icons/play_arrow.svg")

        # Émet le signal pour informer le lecteur
        events.play_pause_signal.emit(self.is_playing)

    def update_timeline(self, current_time, total_time):
        current_formatted = time.strftime("%M:%S", time.gmtime(current_time))
        total_formatted = time.strftime("%M:%S", time.gmtime(total_time))
        self.timeline_label.setText(f"{current_formatted}/{total_formatted}")

    def update_slider_position(self, position_percent):
        """
        Met à jour la position du slider en pourcentage (0-100)
        """
        self.is_programmatic_update = True
        self.progress_slider.setValue(int(position_percent))
        self.is_programmatic_update = False

    def on_slider_value_changed(self, value):
        """
        Appelé quand la valeur du slider change
        value est entre 0 et 100
        """
        if self.is_programmatic_update:
            return

        print(f"[Controls] Slider value changed to {value}%")
        events.seek_signal.emit(value / 100.0)  # Convertit en pourcentage (0-1)

    def on_add_tag(self, timestamp, total_time):
        """
        Ajoute un marqueur de tag sur le slider à la position spécifiée.

        Args:
            timestamp (float): Position temporelle du tag en secondes
            total_time (float): Durée totale de la vidéo en secondes
        """
        if total_time == 0 or timestamp > total_time:
            return

        position = timestamp / total_time
        self.progress_slider.add_tag_marker(position)
