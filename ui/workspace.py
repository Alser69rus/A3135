from PyQt5 import QtWidgets

from opc.server import Server
from ui.graph_widget import Plot
from ui.img_widget import ImageWidget
from ui.main_menu import MainMenu
from ui.report_widget import ReportWidget
from ui.text_widget import TextWidget


class Workspace(QtWidgets.QWidget):
    def __init__(self, server: Server, parent=None):
        super().__init__(parent=parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.setLayout(self.hbox)
        self.hbox.setContentsMargins(4, 4, 4, 4)
        self.menu = MainMenu()
        self.text = TextWidget()
        self.img = ImageWidget()
        self.graph = Plot(server=server)
        self.report = ReportWidget()

        self.hbox.addWidget(self.menu)
        self.hbox.addWidget(self.text)
        self.hbox.addWidget(self.img)
        self.hbox.addWidget(self.graph)
        self.hbox.addWidget(self.report)
