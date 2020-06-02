from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from ui.manometer import Manometer16, Manometer10
from typing import Union, Dict


class Manometers(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.setLayout(self.hbox)
        self.manometer: Dict[str, Union[Manometer10, Manometer16]] = {}

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(150)

        settings = QSettings('Настройки.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')

        keys = ['ppm', 'pim', 'ptc1', 'ptc2', 'pupr']
        names = ['P пм', 'Р им', 'Р тц1', 'Р тц2', 'Р упр рд/сд']

        for i in range(5):
            max_value = float(settings.value(f'Manometers/m{i}', 1.6))
            name = names[i]
            key = keys[i]
            if max_value == 1.6:
                self.manometer[key] = Manometer16(name)
            else:
                self.manometer[key] = Manometer10(name)
            self.hbox.addWidget(self.manometer[key])


