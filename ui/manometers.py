from PyQt5 import QtWidgets


class Manometers(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.hbox = QtWidgets.QHBoxLayout()
        self.manometer_1 = QtWidgets.QWidget()
        self.manometer_2 = QtWidgets.QWidget()
        self.manometer_3 = QtWidgets.QWidget()
        self.manometer_4 = QtWidgets.QWidget()
        self.manometer_5 = QtWidgets.QWidget()

        self.setLayout(self.hbox)
        self.hbox.addWidget(self.manometer_1)
        self.hbox.addWidget(self.manometer_2)
        self.hbox.addWidget(self.manometer_3)
        self.hbox.addWidget(self.manometer_4)
        self.hbox.addWidget(self.manometer_5)

        self.setStyleSheet('QWidget{ background: yellow }')
        self.manometer_1.setStyleSheet('QWidget{ background: red }')
        self.manometer_2.setStyleSheet('QWidget{ background: orange }')
        self.manometer_3.setStyleSheet('QWidget{ background: yellow }')
        self.manometer_4.setStyleSheet('QWidget{ background: green }')
        self.manometer_5.setStyleSheet('QWidget{ background: cyan }')

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumHeight(150)
        self.hbox.setContentsMargins(0, 0, 0, 0)
