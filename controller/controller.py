from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtCore import Qt, QStateMachine
from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtGui import QKeyEvent, QPixmap
from dataclasses import dataclass, field
from typing import List, Dict
from functools import partial

from ui.main_form import MainForm
from opc.server import Server
from ui.menu import MenuWidget
from pyqtgraph import PlotWidget
from opc.opc import AnalogItemType, TwoStateDiscreteType

ANIMATE_CLICK_DELAY = 50


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
        self.btn: Btn = Btn()
        self.form: MainForm = None
        self.server: Server = None
        self.stm: QStateMachine = None

        self.menu: MenuWidget = None
        self.text: QLabel = None
        self.image: QLabel = None
        self.graph: PlotWidget = None
        self.images: Dict[str, QPixmap] = {}
        self.ai: Dict[str, AnalogItemType] = {}
        self.di: Dict[str, TwoStateDiscreteType] = {}

    def connect_form(self, form: MainForm):
        self.form = form
        self.menu = form.workspace.menu
        self.text = form.workspace.text
        self.image = form.workspace.img
        self.images = self.image.images
        self.graph = form.workspace.graph

        self.connect_button_panel(form.btn_panel)
        self.connect_menu(self.menu)
        self.connect_key_press_event(self.form)
        self.form.closeEvent = self.closeEvent

    def connect_button_panel(self, panel):
        self.btn.back = panel.back
        self.btn.up = panel.up
        self.btn.down = panel.down
        self.btn.yes = panel.yes
        self.btn.no = panel.no

    def connect_menu(self, menu):
        self.btn.back.clicked.connect(menu.on_back_click)
        self.btn.yes.clicked.connect(menu.on_ok_click)
        self.btn.up.clicked.connect(menu.on_up_click)
        self.btn.down.clicked.connect(menu.on_down_click)

    def connect_key_press_event(self, form):
        form.keyPressEvent = self.keyPressEvent

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
            elif event.key() == Qt.Key_Enter:
                self.btn.yes.animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Space:
                self.btn.no.animateClick(ANIMATE_CLICK_DELAY)

    def connect_server(self, server: Server):
        self.server = server
        self.ai = server.ai
        self.di = server.di

    def connect_state_machine(self, stm: QStateMachine):
        self.stm = stm

    def closeEvent(self, QCloseEvent):
        running_states = [self.server.th.isRunning(), self.stm.isRunning()]
        self.server.stop_all.emit()
        self.stm.stop()
        if any(running_states):
            QTimer.singleShot(500, self.form.close)
            QCloseEvent.ignore()
        else:
            QCloseEvent.accept()

    def connect_manometers(self):
        manometer = self.form.manometers.manometer
        self.ai['ppm'].value_changed.connect(manometer['ppm'].set_value)
        self.ai['pim'].value_changed.connect(manometer['pim'].set_value)
        self.ai['ptc1'].value_changed.connect(manometer['ptc1'].set_value)
        self.ai['ptc2'].value_changed.connect(manometer['ptc2'].set_value)
        self.ai['pupr'].value_changed.connect(manometer['pupr'].set_value)

    def connect_di_buttons(self):
        self.di['back'].clicked.connect(partial(self.btn.back.animateClick, ANIMATE_CLICK_DELAY))
        self.di['up'].clicked.connect(partial(self.btn.up.animateClick, ANIMATE_CLICK_DELAY))
        self.di['down'].clicked.connect(partial(self.btn.down.animateClick, ANIMATE_CLICK_DELAY))
        self.di['yes'].clicked.connect(partial(self.btn.yes.animateClick, ANIMATE_CLICK_DELAY))
        self.di['no'].clicked.connect(partial(self.btn.no.animateClick, ANIMATE_CLICK_DELAY))
