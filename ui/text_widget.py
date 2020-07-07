from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TextWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFont(QFont('Segoi ui', 14))
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setWordWrap(True)
        self.setMinimumWidth(300)
