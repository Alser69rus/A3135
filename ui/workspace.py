from PyQt5 import QtWidgets
from ui.main_menu import MainMenu
from ui.text_widget import TextWidget


class Workspace(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.menu = MainMenu()
        self.text = TextWidget()
        self.img = QtWidgets.QWidget()
        self.graph = QtWidgets.QWidget()
        self.settings = QtWidgets.QWidget()
        self.report_header = QtWidgets.QWidget()
        self.report = QtWidgets.QWidget()

        self.setLayout(self.hbox)
        self.hbox.addWidget(self.menu)
        self.hbox.addWidget(self.text)
        self.hbox.addWidget(self.img)
        self.hbox.addWidget(self.graph)
        self.hbox.addWidget(self.settings)
        self.hbox.addWidget(self.report_header)
        self.hbox.addWidget(self.report)

        self.img.setStyleSheet('QWidget{ background: yellow }')
        self.graph.setStyleSheet('QWidget{ background:  green}')
        self.settings.setStyleSheet('QWidget{ background: cyan }')
        self.report_header.setStyleSheet('QWidget{ background: blue }')
        self.report.setStyleSheet('QWidget{ background: magenta }')
