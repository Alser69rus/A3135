from PyQt5 import QtWidgets
from ui.manometer import Manometer, Manometer_10


class Manometers(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.manometer = {
            'ppm': Manometer('P пм'),
            'pim': Manometer_10('Р им'),
            'ptc1': Manometer('Р тц1'),
            'ptc2': Manometer('Р тц2'),
            'pupr': Manometer('Р упр рд/сд'),
        }

        self.hbox = QtWidgets.QHBoxLayout()

        self.setLayout(self.hbox)
        self.hbox.addWidget(self.manometer['ppm'])
        self.hbox.addWidget(self.manometer['pim'])
        self.hbox.addWidget(self.manometer['ptc1'])
        self.hbox.addWidget(self.manometer['ptc2'])
        self.hbox.addWidget(self.manometer['pupr'])

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(150)
