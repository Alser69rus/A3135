from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class DInput(QObject):
    updated = pyqtSignal(bool)
    changed = pyqtSignal(bool)
    on = pyqtSignal()
    off = pyqtSignal()
    front = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.value: bool = False

    def get_value(self) -> bool:
        return self.value

    @pyqtSlot(bool)
    def set_value(self, value: bool):
        old_value = self.value
        self.value = value
        if value:
            self.on.emit()
        else:
            self.off.emit()
        if not old_value and value:
            self.front.emit()
        if old_value != value:
            self.changed.emit(value)
        self.updated(value)


class AInput(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._value: float = 0.0
        self._instrument_value: int = 0

