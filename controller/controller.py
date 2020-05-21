from PyQt5.QtCore import QObject, QStateMachine, pyqtSlot, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QKeyEvent
from dataclasses import dataclass, field
from ui.main_form import MainForm

ANIMATE_CLICK_DELAY = 50


@dataclass
class Btn:
    back: QPushButton = field(default_factory=QPushButton)
    up: QPushButton = field(default_factory=QPushButton)
    down: QPushButton = field(default_factory=QPushButton)
    yes: QPushButton = field(default_factory=QPushButton)
    no: QPushButton = field(default_factory=QPushButton)


class Controller(QObject):
    def __init__(self, form: MainForm, state_machine: QStateMachine, parent=None):
        super().__init__(parent=parent)
        self.btn = Btn()
        self.form = form
        self.stm = state_machine
        self.button_panel = self.form.btn_panel
        self.menu = self.form.workspace.menu
        self.text = self.form.workspace.text.text

        self.connect_button_panel()
        self.connect_main_menu()
        self.form.keyPressEvent = self.keyPressEvent

    def connect_button_panel(self):
        self.btn.back = self.button_panel.back
        self.btn.up = self.button_panel.up
        self.btn.down = self.button_panel.down
        self.btn.yes = self.button_panel.yes
        self.btn.no = self.button_panel.no

    def connect_main_menu(self):
        self.btn.back.clicked.connect(self.menu.on_back_click)
        self.btn.yes.clicked.connect(self.menu.on_ok_click)
        self.btn.up.clicked.connect(self.menu.on_up_click)
        self.btn.down.clicked.connect(self.menu.on_down_click)
        self.menu.button_clicked.connect(self.on_menu_button_clicked)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                self.btn.back.animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Up:
                self.btn.up.animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Down:
                self.btn.down.animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Return:
                self.btn.yes.animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Space:
                self.btn.no.animateClick(ANIMATE_CLICK_DELAY)

    def on_menu_button_clicked(self):
        print(self.sender().sender().sender())
