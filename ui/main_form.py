from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QKeyEvent
from ui.button_panel import ButtonPanel
from ui.workspace import Workspace
from ui.manometers_panel import Manometers
from ui.control_window import ControlWindow
from ui.diagnostic_window import DiagnosticWindow

ANIMATE_CLICK_DELAY = 50


class MainForm(QtWidgets.QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.resize(1024, 768)
        self.setWindowTitle('Стенд А3139')

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.manometers = Manometers()
        self.workspace = Workspace()
        self.btn_panel = ButtonPanel(server=server)

        self.setLayout(self.vbox)
        self.vbox.addWidget(self.manometers)
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.btn_panel)

        self.ctrl_win = ControlWindow(server=server)
        self.diag_win = DiagnosticWindow(server=server)



    @pyqtSlot(str)
    def show_panel(self, value: str):
        available_panel = {
            'манометры': self.manometers,
            'меню': self.workspace.menu,
            'текст': self.workspace.text,
            'картинка': self.workspace.img,
            'график': self.workspace.graph,
            'настройки': self.workspace.settings,
            'заголовок': self.workspace.report_header,
            'отчет': self.workspace.report,
        }
        for panel in available_panel.keys():
            available_panel[panel].setVisible(panel in value)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                self.btn_panel.button['back'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Up:
                self.btn_panel.button['up'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Down:
                self.btn_panel.button['down'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Return:
                self.btn_panel.button['yes'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Enter:
                self.btn_panel.button['yes'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_Space:
                self.btn_panel.button['no'].animateClick(ANIMATE_CLICK_DELAY)
            elif event.key() == Qt.Key_F11:
                self.ctrl_win.setVisible(not self.ctrl_win.isVisible())
            elif event.key() == Qt.Key_F12:
                self.diag_win.setVisible(not self.diag_win.isVisible())
