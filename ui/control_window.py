from PyQt5.QtWidgets import QWidget, QDial, QVBoxLayout, QHBoxLayout, QGridLayout, QDoubleSpinBox
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSettings
from typing import Union, List, Dict


class ControlWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Окно эмуляции стенда')
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.manometers = QWidget()
        self.vbox.addWidget(self.manometers)
        self.manometr_layout = QGridLayout()
        self.manometr_layout.setContentsMargins(0, 0, 0, 0)
        self.manometers.setLayout(self.manometr_layout)
        self.manometer: List[Union[DialWidget16, DialWidget10]] = []
        settings = QSettings('Настройки.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        names = ['Р пм', 'Р им', 'Р тц1', 'Р тц2', 'Р упр рд/сд']
        for i in range(5):
            max_value = float(settings.value(f'Manometers/m{i}', 1.6))
            name = names[i]
            if max_value == 1.6:
                self.manometer.append(DialWidget16(name))
            else:
                self.manometer.append(DialWidget10(name))
            self.manometr_layout.addWidget(self.manometer[i], 0, i)

        self.buttons_widget = QWidget()
        self.button_layout = QHBoxLayout()
        self.vbox.addWidget(self.buttons_widget)
        self.buttons_widget.setLayout(self.button_layout)
        buttons = [('back', 'Назад'),
                   ('up', 'Вверх'),
                   ('down', 'Вниз'),
                   ('yes', 'Да'),
                   ('no', 'Нет'),
                   ]
        self.button: Dict[QPushButton] = {}

        for key, name in buttons:
            button = QPushButton(name)
            self.button[key] = button
            self.button_layout.addWidget(button)


class DialWidget16(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, caption: str, parent=None):
        super().__init__(parent=parent)
        self.setFont(QFont('Segoi UI', 14))
        self.setFixedWidth(150)
        self.setFixedHeight(180)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)
        self.caption = QLabel(caption)
        self.caption.setFont(QFont('Segoi UI', 14))
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
