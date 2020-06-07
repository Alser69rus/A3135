from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QKeyEvent
from typing import Dict
from ui.button_panel import ButtonPanel
from ui.workspace import Workspace
from ui.manometers_panel import ManometersPanel
from ui.control_window import ControlWindow
from ui.diagnostic_window import DiagnosticWindow

ANIMATE_CLICK_DELAY = 50


class MainForm(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(1024,768)
        self.setWindowTitle('Стенд А3139')

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.workspace = Workspace()
        self.panel: Dict[str, QWidget] = {
            'манометры': ManometersPanel(server=server),
            'меню': self.workspace.menu,
            'текст': self.workspace.text,
            'картинка': self.workspace.img,
            'график': self.workspace.graph,
            'отчет': self.workspace.report,
        }

        self.button_panel = ButtonPanel(server=server)

        self.setLayout(self.vbox)
        self.vbox.addWidget(self.panel['манометры'])
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.button_panel)

        self.ctrl_win = ControlWindow(server=server)
        self.diag_win = DiagnosticWindow(server=server)
        self.connect_menu()

    @pyqtSlot(str)
    def show_panel(self, value: str):
        for key in self.panel.keys():
            self.panel[key].setVisible(key in value)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                self.button_panel.button['back'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Up:
                self.button_panel.button['up'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Down:
                self.button_panel.button['down'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Return:
                self.button_panel.button['yes'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Enter:
                self.button_panel.button['yes'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Space:
                self.button_panel.button['no'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_F11:
                self.ctrl_win.setVisible(not self.ctrl_win.isVisible())
            elif event.key() == Qt.Key_F12:
                self.diag_win.setVisible(not self.diag_win.isVisible())

    def connect_menu(self):
        menu = self.workspace.menu
        self.button_panel.button['back'].clicked.connect(menu.on_back_click)
        self.button_panel.button['up'].clicked.connect(menu.on_up_click)
        self.button_panel.button['down'].clicked.connect(menu.on_down_click)
        self.button_panel.button['yes'].clicked.connect(menu.on_ok_click)
