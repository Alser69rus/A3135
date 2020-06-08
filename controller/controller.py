from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtCore import QStateMachine
from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from typing import Dict, Union

from ui.main_form import MainForm
from opc.server import Server
from ui.menu import MenuWidget
from ui.main_menu import MainMenu
from pyqtgraph import PlotWidget
from opc.opc import TwoStateDiscreteType
from modules.btp.data import BtpData

ANIMATE_CLICK_DELAY = 50


class Controller(QObject):
    close_all = pyqtSignal()
    server_updated = pyqtSignal()

    def __init__(self, server: Server, form: MainForm, stm: QStateMachine, parent=None):
        super().__init__(parent=parent)
        self.server = server
        self.form = form
        self.stm = stm

        self.menu: MainMenu = form.workspace.menu
        self.text: QLabel = form.workspace.text
        self.image: QLabel = form.workspace.img
        self.graph: PlotWidget = form.workspace.graph
        self.images: Dict[str, QPixmap] = form.workspace.img.images
        self.ctrl_win: QWidget = form.ctrl_win
        self.diag_win: QWidget = form.diag_win

        self.show_panel = form.show_panel
        self.show_menu = self.menu.show_menu
        self.reset_prepare = self.menu.reset_prepare
        self.button_enable = self.form.button_panel.button_enable
        self.setText = self.text.setText

        self.form.closeEvent = self.closeEvent
        self.close_all.connect(self.ctrl_win.close)
        self.close_all.connect(self.diag_win.close)
        self.server.worker.updated.connect(self.server_updated)

        self.button: Dict[str, Union[TwoStateDiscreteType, QPushButton]] = {}
        panel_buttons = self.form.button_panel.button.keys()
        server_buttons = server.button.keys()
        for key in server_buttons:
            if key in panel_buttons:
                self.button[key] = form.button_panel.button[key]
            else:
                self.button[key] = server.button[key]

        self.manometer = server.manometer
        self.switch = server.switch
        self.switch_with_neutral = server.switch_with_neutral

        self.btp=BtpData()


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
