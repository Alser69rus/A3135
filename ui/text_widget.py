from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TextWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vbox = QVBoxLayout()
        self.text = QLabel()
        self.text.setFont(QFont('Segoi ui', 14))
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.text)
