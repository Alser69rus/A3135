from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtCore import Qt, QStateMachine
from PyQt5.QtWidgets import QPushButton, QLabel, QRadioButton, QWidget
from PyQt5.QtGui import QKeyEvent, QPixmap
from dataclasses import dataclass, field
from typing import List, Dict
from functools import partial

from ui.main_form import MainForm
from opc.server import Server
from ui.menu import MenuWidget
from pyqtgraph import PlotWidget
from opc.opc import AnalogItemType, TwoStateDiscreteType
from ui.control_window import ControlWindow
from ui.diagnostic_window import DiagnosticWindow

ANIMATE_CLICK_DELAY = 50


@dataclass
class Btn:
    back: QPushButton = field(default_factory=QPushButton)
    up: QPushButton = field(default_factory=QPushButton)
    down: QPushButton = field(default_factory=QPushButton)
    yes: QPushButton = field(default_factory=QPushButton)
    no: QPushButton = field(default_factory=QPushButton)


class Controller(QObject):
    close_all = pyqtSignal()

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
        self.ctrl_win: QWidget = None
        self.diag_win: QWidget = None

        self.show_panel = None
        self.show_menu = None

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
        self.show_panel = self.form.show_panel
        self.show_menu = self.menu.show_menu

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
            elif event.key() == Qt.Key_F11:
                if self.ctrl_win is None:
                    return
                state = not self.ctrl_win.isVisible()
                self.ctrl_win.setVisible(state)
                self.server.worker.skip_update = state

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
        self.close_all.emit()
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

    def connect_control_window(self, win: ControlWindow):
        self.ctrl_win = win
        self.close_all.connect(win.close)

        for key in win.manometer.keys():
            win.manometer[key].valueChanged.connect(self.ai[key].set_value)

        for key in win.button.keys():
            button: QPushButton = win.button[key]
            button.clicked.connect(self.di[key].clicked)

        for key in win.switch.keys():
            switch: QPushButton = win.switch[key]
            switch.toggled.connect(self.di[key].set_value)

        radio = {
            '0 - rd 042': win.radio['РД 042 - 0 - КЭБ 208'].button['РД 042'],
            '0 - keb 208': win.radio['РД 042 - 0 - КЭБ 208'].button['КЭБ 208'],
            '0- vr': win.radio['ВР - 0 - КУ'].button['ВР'],
            '0- ku': win.radio['ВР - 0 - КУ'].button['КУ'],
        }
        for key in radio.keys():
            radio_button: QRadioButton = radio[key]
            radio_button.toggled.connect(self.di[key].set_value)

    def connect_diagnostic_window(self, win: DiagnosticWindow):
        self.diag_win = win
        self.close_all.connect(win.close)

        for key in win.manometers.keys():
            self.ai[key].value_changed.connect(win.manometers[key].set_value)

        for key in win.buttons.keys():
            self.di[key].clicked.connect(partial(win.buttons[key].animateClick, ANIMATE_CLICK_DELAY))

        for key in win.switches.keys():
            self.di[key].value_changed.connect(win.switches[key].setChecked)
