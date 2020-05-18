from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QKeyEvent
from ui.button_panel import ButtonPanel
from dataclasses import dataclass, field


@dataclass
class Btn:
    back: QPushButton = field(default_factory=QPushButton)
    up: QPushButton = field(default_factory=QPushButton)
    down: QPushButton = field(default_factory=QPushButton)
    yes: QPushButton = field(default_factory=QPushButton)
    no: QPushButton = field(default_factory=QPushButton)


class Controller(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.btn = Btn()
        self.btn_panel = None

    def connect_button_panel(self, button_panel: ButtonPanel):
        self.btn_panel = button_panel
        self.btn.back = button_panel.back
        self.btn.up = button_panel.up
        self.btn.down = button_panel.down
        self.btn.yes = button_panel.yes
        self.btn.no = button_panel.no

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                self.btn.back.animateClick(50)
            elif event.key() == Qt.Key_Up:
                self.btn.up.animateClick(50)
            elif event.key() == Qt.Key_Down:
                self.btn.down.animateClick(50)
            elif event.key() == Qt.Key_Return:
                self.btn.yes.animateClick(50)
            elif event.key() == Qt.Key_Space:
                self.btn.no.animateClick(50)
