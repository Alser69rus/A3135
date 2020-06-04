from PyQt5.QtWidgets import QWidget, QDial, QVBoxLayout, QHBoxLayout, QGridLayout, QDoubleSpinBox
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QRadioButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSettings, Qt
from typing import Union, List, Dict
from PyQt5 import QtGui

FONT_SIZE = 12


class DiagnosticWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Окно проверки сигналов стенда')
        self.grid = QGridLayout()
        self.setFont(QFont('Segoi UI', FONT_SIZE))
        self.setLayout(self.grid)
        manometers = [
            ('ppm', 'Р пм'),
            ('pim', 'Р им',),
            ('ptc1', 'Р тц1',),
            ('ptc2', 'Р тц2',),
            ('pupr', 'Р упр рд/сд',),
        ]
        self.manometers: Dict[str, FloatLabel] = {}
        for i, (key, name) in enumerate(manometers):
            caption = QLabel(name)
            manometer = FloatLabel('0.000')
            self.manometers[key] = manometer
            caption.setAlignment(Qt.AlignCenter)
            manometer.setAlignment(Qt.AlignCenter)
            manometer.setStyleSheet(
                f'QLabel {{'
                f'font-size:{FONT_SIZE}pt;'
                f'border:2px;'
                f'border-radius:8px;'
                f'border-color:black;'
                f'text-align:center;'
                f'padding: 4px;'
                f'border-style: solid;'
                f'background-color: rgba(0,0,100,10%);}}'
            )
            self.grid.addWidget(caption, 0, i)
            self.grid.addWidget(manometer, 1, i)

        switches = [
            ('ku 215', 'КУ 215'),
            ('el. braking', 'ЗАМ. ЭЛ. ТОРМ.'),
            ('>60 km/h', '> 60 км/ч'),
            ('rd 042', 'РД 042'),
            ('upr rd 042', 'УПР. РД 042'),
            ('keb 208', 'КЭБ 208'),
            ('red 211', 'РЕД 211.020'),
            ('leak 1', 'УТЕЧКА d 1'),
            ('leak 0,5', 'УТЕЧКА d 0.5'),
        ]
        self.switches: Dict[str, QPushButton] = {}
        for i, (key, name) in enumerate(switches):
            switch = QPushButton(name)
            self.switches[key] = switch
            switch.setCheckable(True)
            switch.setStyleSheet(
                f'QPushButton {{'
                f'font-size:{FONT_SIZE}pt;'
                f'border:2px;'
                f'border-radius:8px;'
                f'border-color:black;'
                f'text-align:center;'
                f'padding: 4px;'
                f'border-style: solid;'
                f'background-color: rgba(50,0,0,10%);}}'
                f'QPushButton:checked {{'
                f'background-color: rgba(0,200,0,50%);}}'
            )
            self.grid.addWidget(switch, 2 + i // 5, 0 + i % 5)

        buttons = [('back', 'Возврат'),
                   ('up', 'Вверх'),
                   ('down', 'Вниз'),
                   ('yes', 'Да'),
                   ('no', 'Нет'),
                   ('examination', 'Испытание'),
                   ('ok', 'ОК'),
                   ('auto release', 'АВТ ОТПУСК'),
                   ]
        self.buttons: Dict[str, QPushButton] = {}
        for i, (key, name) in enumerate(buttons):
            button = QPushButton(name)
            button.setFlat(True)
            button.setStyleSheet(
                f'QPushButton {{'
                f'font-size:{FONT_SIZE}pt;'
                f'border:2px;'
                f'border-radius:8px;'
                f'border-color:black;'
                f'text-align:center;'
                f'padding: 4px;'
                f'border-style: solid;'
                f'background-color: rgba(200,200,0,10%);}}'
                f'QPushButton:pressed {{'
                f'background-color: rgba(0,200,0,50%);}}'
            )
            self.buttons[key] = button
            self.grid.addWidget(button, 4+i//5, i%5)


class FloatLabel(QLabel):
    @pyqtSlot(float)
    def set_value(self, value: float):
        self.setText(f'{value:5.3f}')
