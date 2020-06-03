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

        manometers = [
            ('ppm', 'Р пм'),
            ('pim', 'Р им',),
            ('ptc1', 'Р тц1',),
            ('ptc2', 'Р тц2',),
            ('pupr', 'Р упр рд/сд',),
        ]

        for key, name in manometers:
            max_value = float(settings.value(f'Manometers/m{key}', 1.6))
            if max_value == 1.6:
                manometer = Manometer16(name)
            else:
                manometer = Manometer10(name)
            self.manometer[key] = manometer
            self.hbox.addWidget(manometer)
