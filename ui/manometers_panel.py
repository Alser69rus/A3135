from PyQt5 import QtWidgets
from ui.manometer import Manometer
from typing import Union, Dict


class ManometersPanel(QtWidgets.QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.setLayout(self.hbox)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.manometer: Dict[str, Manometer] = {}

        for key in server.manometer.keys():
            manometer = Manometer(server.manometer[key])
            self.setMinimumHeight(manometer.height()+4)
            self.manometer[key] = manometer
            self.hbox.addWidget(manometer)

