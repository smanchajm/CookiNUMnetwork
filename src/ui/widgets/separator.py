from PySide6.QtWidgets import QFrame


class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_appearance()

    def _setup_appearance(self):
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #E0E0E0;
                border: none;
                height: 1px;
            }
        """
        )
        self.setFixedHeight(1)
        self.setContentsMargins(0, 0, 0, 8)
