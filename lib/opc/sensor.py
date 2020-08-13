from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from lib.opc.io import DInput


class Button(QObject):
    click = pyqtSignal

    def __init__(self, pin: DInput, parent=None):
        super().__init__(parent=parent)
        self.pin: DInput = pin
        pin.front.connect(self.click)


class Switch(QObject):
    on = pyqtSignal()
    off = pyqtSignal()

    def __init__(self, pin: DInput, parent=None):
        super().__init__(parent=parent)
        self.pin = pin
        pin.on.connect(self.on)
        pin.off.connect(self.off)


class SwitchWithNeutral(QObject):
    zero = pyqtSignal()
    one = pyqtSignal()
    two = pyqtSignal()
    updated = pyqtSignal(int)

    def __init__(self, pin1: DInput, pin2: DInput, parent=None):
        super().__init__(parent=parent)
        self.table = (
            (0, 1),
            (2, 0),
        )
        self.value = [0, 0]
        self.signal = (self.zero, self.one, self.two)
        pin1.updated.connect(self.pin1_update)
        pin2.updated.connect(self.pin2_update)

    @pyqtSlot(bool)
    def pin1_update(self, value: bool):
        self.value[0] = 1 if value else 0

    @pyqtSlot(bool)
    def pin2_update(self, value: bool):
        self.value[1] = 1 if value else 0

    def get_state(self):
        return self.table[self.value[1]][self.value[0]]

    @pyqtSlot(bool)
    def update(self):
        state = self.get_state()
        self.signal[state].emit()
        self.updated.emit(state)
