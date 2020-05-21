from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from typing import List


class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.img = QLabel()
        self.img.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.img)
        self.images: List[QPixmap] = {}
