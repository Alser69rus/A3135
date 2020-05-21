from PyQt5 import QtWidgets
from ui.main_menu import MainMenu
from ui.text_widget import TextWidget
from ui.img_widget import ImageWidget
from ui.graph_widget import Plot


class Workspace(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.setLayout(self.hbox)
        self.hbox.setContentsMargins(4, 4, 4, 4)
        self.menu = MainMenu()
        self.text = TextWidget()
        self.img = ImageWidget()
        self.graph = Plot()
        self.settings = QtWidgets.QWidget()
        self.report_header = QtWidgets.QWidget()
        self.report = QtWidgets.QWidget()


        self.hbox.addWidget(self.menu)
        self.hbox.addWidget(self.text)
        self.hbox.addWidget(self.img)
        self.hbox.addWidget(self.graph)
        self.hbox.addWidget(self.settings)
        self.hbox.addWidget(self.report_header)
        self.hbox.addWidget(self.report)


        self.settings.setStyleSheet('QWidget{ background: cyan }')
        self.report_header.setStyleSheet('QWidget{ background: blue }')
        self.report.setStyleSheet('QWidget{ background: magenta }')
