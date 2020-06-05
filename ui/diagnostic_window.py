from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtCore import pyqtSlot, Qt
from typing import Dict, List
from functools import partial
from opc.opc import AnalogItemType, TwoStateWithNeutralType, TwoStateDiscreteType

FONT_SIZE = 12
ANIMATE_CLICK_DELAY = 50


class DiagnosticWindow(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Окно проверки сигналов стенда')
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.setFont(QFont('Segoi UI', FONT_SIZE))

        self.manometers_panel = ManometersPanel(manometers=server.manometer)
        self.vbox.addWidget(self.manometers_panel)

        self.switch_panel = SwitchesPanel(switches=server.switch)
        self.vbox.addWidget(self.switch_panel)

        self.switch_with_neutral_panel = SwitchesWithNeutralPanel(switches=server.switch_with_neutral)
        self.vbox.addWidget(self.switch_with_neutral_panel)

        self.buttons_panel = ButtonsPanel(buttons=server.button)
        self.vbox.addWidget(self.buttons_panel)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_F12:
            self.setVisible(False)


class ManometersPanel(QWidget):
    def __init__(self, manometers: Dict[str, AnalogItemType], parent=None):
        super().__init__(parent=parent)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.manometers: Dict[str, ManometerWidget] = {}
        for key in manometers.keys():
            manometer = ManometerWidget(manometer=manometers[key])
            self.manometers[key] = manometer
            self.hbox.addWidget(manometer)


class ManometerWidget(QWidget):
    def __init__(self, manometer: AnalogItemType, parent=None):
        super().__init__(parent=parent)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.title = QLabel(manometer.name)
        self.vbox.addWidget(self.title)
        self.title.setAlignment(Qt.AlignCenter)
        self.text = QLabel('0.000')
        self.vbox.addWidget(self.text)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet(
            f'QLabel {{'
            f'font-size:{FONT_SIZE}pt;'
            f'border:2px;'
            f'border-radius:8px;'
            f'border-color:black;'
            f'text-align:center;'
            f'padding: 4px;'
            f'border-style: solid;'
            f'background-color: rgba(0,0,100,10%);'
            f'}}'
        )
        manometer.value_changed.connect(self.set_value)

    @pyqtSlot(float)
    def set_value(self, value: float):
        self.text.setText(f'{value:5.3f}')


class SwitchesPanel(QWidget):
    def __init__(self, switches: Dict[str, TwoStateDiscreteType], parent=None):
        super().__init__(parent=parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.switches: Dict[str, SwitchWidget] = {}
        for i, key in enumerate(switches.keys()):
            switch = SwitchWidget(switch=switches[key])
            self.switches[key] = switch
            self.grid.addWidget(switch, i // 5, i % 5)


class SwitchWidget(QPushButton):
    def __init__(self, switch: TwoStateDiscreteType, parent=None):
        super().__init__(parent=parent)
        self.setText(switch.name)
        self.setCheckable(True)
        switch.value_changed.connect(self.setChecked)
        self.setStyleSheet(
            f'QPushButton {{'
            f'font-size:{FONT_SIZE}pt;'
            f'border:2px;'
            f'border-radius:8px;'
            f'border-color:black;'
            f'text-align:center;'
            f'padding: 4px;'
            f'border-style: solid;'
            f'background-color: rgba(50,0,0,10%);'
            f'}}'
            f'QPushButton:checked {{'
            f'background-color: rgba(0,200,0,50%);'
            f'}}'
        )


class ButtonsPanel(QWidget):
    def __init__(self, buttons: Dict[str, TwoStateDiscreteType], parent=None):
        super().__init__(parent=parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.buttons: Dict[str, ButtonWidget] = {}
        for i, key in enumerate(buttons.keys()):
            button = ButtonWidget(button=buttons[key])
            self.buttons[key] = button
            self.grid.addWidget(button, i // 5, i % 5)


class ButtonWidget(QPushButton):
    def __init__(self, button: TwoStateDiscreteType, parent=None):
        super().__init__(parent=parent)
        self.setText(button.name)
        self.setFlat(True)
        button.clicked.connect(partial(self.animateClick, ANIMATE_CLICK_DELAY))
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
        switch.value_changed.connect(self.set_value)

    @pyqtSlot(int)
    def set_value(self, value: int):
        if value==1:
            self.buttons[1].setChecked(True)
        elif value==2:
            self.buttons[2].setChecked(True)
        else:
            self.buttons[0].setChecked(True)
