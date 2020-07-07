from PyQt5 import QtWidgets

from opc.server import Server
from ui.graph_widget import Plot
from ui.img_widget import ImageWidget
from ui.main_menu import MainMenu
from ui.report_widget import ReportWidget
from ui.text_widget import TextWidget


class Workspace(QtWidgets.QSplitter):
    def __init__(self, server: Server, parent=None):
        super().__init__(parent=parent)

        # self.hbox = QtWidgets.QHBoxLayout()
        # self.setLayout(self.hbox)
        # self.hbox.setContentsMargins(4, 4, 4, 4)
        self.setContentsMargins(4,4,4,4)
        self.menu = MainMenu()
        self.text = TextWidget()
        self.img = ImageWidget()

        self.graph = Plot(server=server)

        self.report = ReportWidget()

        self.addWidget(self.menu)
        self.addWidget(self.text)
        self.addWidget(self.img)
        self.addWidget(self.graph)
        self.addWidget(self.report)
