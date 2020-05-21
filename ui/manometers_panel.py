from PyQt5 import QtWidgets
from ui.manometer import Manometer,Manometer_10


class Manometers(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.hbox = QtWidgets.QHBoxLayout()
        self.p_pm = Manometer('P пм')
        self.p_im = Manometer_10('Р им')
        self.p_tc1 = Manometer('Р тц1')
        self.p_tc2 = Manometer('Р тц2')
        self.p_upr = Manometer('Р упр рд/сд')

        self.setLayout(self.hbox)
        self.hbox.addWidget(self.p_pm)
        self.hbox.addWidget(self.p_im)
        self.hbox.addWidget(self.p_tc1)
        self.hbox.addWidget(self.p_tc2)
        self.hbox.addWidget(self.p_upr)

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumHeight(150)
        self.hbox.setContentsMargins(0, 0, 0, 0)

