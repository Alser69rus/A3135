from PyQt5.QtWidgets import QWidget, QDial, QVBoxLayout, QHBoxLayout, QGridLayout, QDoubleSpinBox
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QRadioButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSettings, Qt
from typing import Union, List, Dict
from PyQt5 import QtGui

FONT_SIZE = 12
DIAL_WIDTH = 120
DIAL_HEIGHT = 150


class ControlWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Окно эмуляции стенда')
        self.vbox = QVBoxLayout()
        self.setFont(QFont('Segoi UI', FONT_SIZE))
        self.setLayout(self.vbox)
        self.manometers = QWidget()
        self.vbox.addWidget(self.manometers)
        self.manometr_layout = QHBoxLayout()
        self.manometr_layout.setContentsMargins(0, 0, 0, 0)
        self.manometers.setLayout(self.manometr_layout)

        settings = QSettings('Настройки.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        manometers = [
            ('ppm', 'Р пм'),
            ('pim', 'Р им',),
            ('ptc1', 'Р тц1',),
            ('ptc2', 'Р тц2',),
            ('pupr', 'Р упр рд/сд',),
        ]
        self.manometer: Dict[str, Union[DialWidget16, DialWidget10]] = {}

        for key, name in manometers:
            max_value = float(settings.value(f'Manometers/{key}', 1.6))
            if max_value == 1.6:
                manometer = DialWidget16(name)
            else:
                manometer = DialWidget10(name)
            self.manometer[key] = manometer
            self.manometr_layout.addWidget(manometer)

        self.switches_widget = QWidget()
        self.vbox.addWidget(self.switches_widget)
        self.switches_layout = QGridLayout()
        self.switches_widget.setLayout(self.switches_layout)
        self.switch: Dict[str, QPushButton] = {}
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

        for i, (key, name) in enumerate(switches):
            switch = QPushButton(name)
            switch.setFont(self.font())
            switch.setStyleSheet(f'QPushButton {{border:2px;'
                                 f'border-radius:8px;'
                                 f'border-color:black;'
                                 f'text-align:center;'
                                 f'padding: 4px;'
                                 f'border-style: solid;'
                                 f'background-color: rgba(50,0,0,10%);}}'
                                 f'QPushButton:checked {{'
                                 f'background-color: rgba(0,200,0,50%);}}'
                                 )
            self.switch[key] = switch
            switch.setFlat(True)
            switch.setCheckable(True)
            self.switches_layout.addWidget(switch, i // 3, i % 3)

        self.radio_widget = QWidget()
        self.vbox.addWidget(self.radio_widget)
        self.radio_layout = QHBoxLayout()
        self.radio_widget.setLayout(self.radio_layout)

        radio = [
            ('РД 042', ' - 0 - ', 'КЭБ 208',),
            ('ВР', ' - 0 - ', 'КУ',),
        ]

        self.radio: Dict[str, QGroupBox] = {}
        self.group_box_layout: List[QVBoxLayout] = []

        for buttons in radio:
            name = ''.join(buttons)
            group_box = QGroupBox(name)
            self.radio[name] = group_box
            self.radio_layout.addWidget(group_box)
            layout = QVBoxLayout()
            self.group_box_layout.append(layout)
            group_box.setLayout(layout)
            group_box.button = {}
            for name in buttons:
                button = QRadioButton(name)
                layout.addWidget(button)
                group_box.button[name] = button
                if name == ' - 0 - ':
                    button.setChecked(True)

        self.buttons_widget = QWidget()
        self.button_layout = QGridLayout()
        self.vbox.addWidget(self.buttons_widget)
        self.buttons_widget.setLayout(self.button_layout)
        buttons = [('back', 'Возврат'),
                   ('up', 'Вверх'),
                   ('down', 'Вниз'),
                   ('yes', 'Да'),
                   ('no', 'Нет'),
                   ('examination', 'Испытание'),
                   ('ok', 'ОК'),
                   ('auto release', 'АВТ ОТПУСК'),
                   ]
        self.button: Dict[str, QPushButton] = {}

        for i, (key, name) in enumerate(buttons):
            button = QPushButton(name)
            self.button[key] = button
            self.button_layout.addWidget(button, i // 5, i % 5)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_F11:
            self.setVisible(False)


class DialWidget16(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, caption: str, parent=None):
        super().__init__(parent=parent)
        self.setFont(QFont('Segoi UI', FONT_SIZE))
        self.setFixedWidth(DIAL_WIDTH)
        self.setFixedHeight(DIAL_HEIGHT)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)
        self.caption = QLabel(caption)
        self.caption.setFont(QFont('Segoi UI', FONT_SIZE))
        self.caption.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.caption)
        self.dial = QDial()
        self.vbox.addWidget(self.dial)
        self.dial.setMinimum(0)
        self.dial.setMaximum(160)
        self.dial.setValue(0)
        self.dial.setNotchTarget(2)
        self.dial.setNotchesVisible(True)
        self.spin_box = QDoubleSpinBox()
        self.vbox.addWidget(self.spin_box)
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(1.6)
        self.spin_box.setValue(0)
        self.spin_box.setDecimals(2)
        self.spin_box.setSingleStep(0.01)
        self.spin_box.valueChanged.connect(self.on_spin_box_value_changed)
        self.dial.valueChanged.connect(self.on_dial_value_changed)

    @pyqtSlot(float)
    def on_spin_box_value_changed(self, value: float):
        v = round(value * 100)
        self.dial.setValue(v)
        self.emit_signal(value)

    @pyqtSlot(int)
    def on_dial_value_changed(self, value: int):
        v = value / 100
        self.spin_box.setValue(v)
        self.emit_signal(v)

    def emit_signal(self, value: float):
        value_ofset = value - self.spin_box.minimum()
        value_range = self.spin_box.maximum() - self.spin_box.minimum()
        value_percent = value_ofset / value_range
        signal = round(value_percent * 16000 + 4000)
        self.valueChanged.emit(signal)


class DialWidget10(DialWidget16):
    def __init__(self, caption: str, parent=None):
        super().__init__(caption=caption, parent=parent)
        self.dial.setMaximum(100)
        self.spin_box.setMaximum(1.0)
