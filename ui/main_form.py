from functools import partial
from typing import Dict

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QKeyEvent, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar

from ui.button_panel import ButtonPanel
from ui.control_window import ControlWindow
from ui.diagnostic_window import DiagnosticWindow
from ui.manometers_panel import ManometersPanel
from ui.workspace import Workspace

ANIMATE_CLICK_DELAY = 50


class MainForm(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        # self.setMaximumHeight(700)
        self.setFixedSize(1366, 700)
        self.setWindowTitle('Стенд А3135')
        self.setWindowIcon(QIcon('A3135.ico'))

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.workspace = Workspace(server=server)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)

        self.panel: Dict[str, QWidget] = {
            'манометры': ManometersPanel(server=server),
            'меню': self.workspace.menu,
            'текст': self.workspace.text,
            'картинка': self.workspace.img,
            'график': self.workspace.graph,
            'отчет': self.workspace.report,
            'прогресс': self.progress_bar,
        }

        self.button_panel = ButtonPanel(server=server)
        self.workspace.report.up.connect(partial(self.button_panel.button['up'].animateClick, ANIMATE_CLICK_DELAY))
        self.workspace.report.down.connect(partial(self.button_panel.button['down'].animateClick, ANIMATE_CLICK_DELAY))

        self.setLayout(self.vbox)
        self.vbox.addWidget(self.panel['манометры'])
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.progress_bar)
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

        self.button_panel.button['back'].clicked.connect(self.workspace.report.menu.on_back_click)
        self.button_panel.button['up'].clicked.connect(self.workspace.report.menu.on_up_click)
        self.button_panel.button['down'].clicked.connect(self.workspace.report.menu.on_down_click)
        self.button_panel.button['yes'].clicked.connect(self.workspace.report.menu.on_ok_click)
