from PyQt5.QtWidgets import QWidget, QDial, QVBoxLayout, QHBoxLayout, QGridLayout, QDoubleSpinBox
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QRadioButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from typing import Dict, List
from PyQt5 import QtGui
from opc.opc import AnalogItemType, TwoStateWithNeutralType, TwoStateDiscreteType

FONT_SIZE = 12
DIAL_WIDTH = 120
DIAL_HEIGHT = 150


class ControlWindow(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.server = server
        server.worker.updated.connect(self.emulate_server_update)
        self.setWindowTitle('Окно эмуляции стенда')
        self.vbox = QVBoxLayout()
        self.setFont(QFont('Segoi UI', FONT_SIZE))
        self.setLayout(self.vbox)

        self.manometers_panel = ManometersPanel(manometers=server.manometer)
        self.vbox.addWidget(self.manometers_panel)

        self.switches_panel = SwitchesPanel(switches=server.switch)
        self.vbox.addWidget(self.switches_panel)

        self.switches_with_neutral_panel = SwitchesWithNeutralPanel(switches=server.switch_with_neutral)
        self.vbox.addWidget(self.switches_with_neutral_panel)

        self.buttons_panel = ButtonsPanel(buttons=server.button)
        self.vbox.addWidget(self.buttons_panel)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_F11:
            self.setVisible(False)

    @pyqtSlot()
    def emulate_server_update(self):
        if self.isVisible():
            self.server.worker.skip_update = True
            for key in self.server.switch.keys():
                switch = self.server.switch[key]
                switch.set_value(switch.get_value())
            for key in self.server.switch_with_neutral.keys():
                switch = self.server.switch_with_neutral[key]
                switch.set_value(switch.get_value())
        else:
            self.server.worker.skip_update = False


class DialWidget(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, manometer: AnalogItemType, parent=None):
        super().__init__(parent=parent)
        self.setFont(QFont('Segoi UI', FONT_SIZE))
        self.setFixedWidth(DIAL_WIDTH)
        self.setFixedHeight(DIAL_HEIGHT)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)
        self.caption = QLabel(manometer.name)
        self.caption.setFont(QFont('Segoi UI', FONT_SIZE))
        self.caption.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.caption)
        self.dial = QDial()
        self.vbox.addWidget(self.dial)
        self.dial.setMinimum(0)
        self.dial.setMaximum(round(manometer.eu_range.high * 100))
        self.dial.setValue(0)
        self.dial.setNotchTarget(2)
        self.dial.setNotchesVisible(True)
        self.spin_box = QDoubleSpinBox()
        self.vbox.addWidget(self.spin_box)
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(manometer.eu_range.high)
        self.spin_box.setValue(0)
        self.spin_box.setDecimals(2)
        self.spin_box.setSingleStep(0.01)
        self.spin_box.valueChanged.connect(self.on_spin_box_value_changed)
        self.dial.valueChanged.connect(self.on_dial_value_changed)
        self.valueChanged.connect(manometer.set_value)

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


class ManometersPanel(QWidget):
    def __init__(self, manometers: Dict[str, AnalogItemType], parent=None):
        super().__init__(parent=parent)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.manometer: Dict[str, DialWidget] = {}

        for key in manometers.keys():
            manometer = DialWidget(manometer=manometers[key])
            self.manometer[key] = manometer
            self.hbox.addWidget(manometer)


class SwitchesPanel(QWidget):
    def __init__(self, switches: Dict[str, TwoStateDiscreteType], parent=None):
        super().__init__(parent=parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.switch: Dict[str, SwitchWidget] = {}
        for i, key in enumerate(switches.keys()):
            switch = SwitchWidget(switch=switches[key])
            self.switch[key] = switch
            self.grid.addWidget(switch, i // 3, i % 3)


class SwitchWidget(QPushButton):
    def __init__(self, switch: TwoStateDiscreteType, parent=None):
        super().__init__(parent=parent)
        self.setText(switch.name)
        self.setFlat(True)
        self.setCheckable(True)
        self.toggled.connect(switch.set_value)
        self.setStyleSheet(f'QPushButton {{'
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


class SwitchesWithNeutralPanel(QWidget):
    def __init__(self, switches: Dict[str, TwoStateWithNeutralType], parent=None):
        super().__init__(parent=parent)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.switch: Dict[str, SwitchWithNeutralWidget] = {}

        for key in switches.keys():
            switch = SwitchWithNeutralWidget(switch=switches[key])
            self.switch[key] = switch
            self.hbox.addWidget(switch)


class SwitchWithNeutralWidget(QGroupBox):
    def __init__(self, switch: TwoStateWithNeutralType, parent=None):
        super().__init__(parent=parent)
        self.setTitle(switch.name)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.buttons: List[QPushButton] = []
        for value in switch.enum_values:
            button = QPushButton(value)
            self.buttons.append(button)
            button.setFlat(True)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setStyleSheet(
                f'QPushButton {{'
                f'font-size:{FONT_SIZE}pt;'
                f'border:2px;'
                f'border-radius:8px;'
                f'border-color:black;'
                f'text-align:center;'
                f'padding: 4px;'
                f'border-style: solid;'
                f'background-color: rgba(50,0,100,10%);}}'
                f'QPushButton:checked {{'
                f'background-color: rgba(0,200,100,50%);}}'
            )

        self.vbox.addWidget(self.buttons[1])
        self.vbox.addWidget(self.buttons[0])
        self.vbox.addWidget(self.buttons[2])
        self.buttons[0].setChecked(True)
        self.buttons[1].toggled.connect(switch.set_state1)
        self.buttons[2].toggled.connect(switch.set_state2)


class ButtonsPanel(QWidget):
    def __init__(self, buttons: Dict[str, TwoStateDiscreteType], parent=None):
        super().__init__(parent=parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.button: Dict[str, ButtonWidget] = {}

        for i, key in enumerate(buttons.keys()):
            button = ButtonWidget(button=buttons[key])
            self.button[key] = button
            self.grid.addWidget(button, i // 5, i % 5)


class ButtonWidget(QPushButton):
    def __init__(self, button: TwoStateDiscreteType, parent=None):
        super().__init__(parent=parent)
        self.setText(button.name)
        self.clicked.connect(button.clicked)
        self.setFlat(True)
        self.setStyleSheet(
            f'QPushButton {{'
            f'font-size:{FONT_SIZE}pt;'
            f'border:2px;'
            f'border-radius:8px;'
            f'border-color:black;'
            f'text-align:center;'
            f'padding: 4px;'
            f'border-style: solid;'
            f'background-color: rgba(200,200,0,10%);'
            f'}}'
            f'QPushButton:pressed {{'
            f'background-color: rgba(0,200,0,50%);'
            f'}}'
        )
