from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import logging
from datetime import datetime
from dataclasses import dataclass


@dataclass()
class Range:
    low: float = 0.0
    high: float = 1.0


class AnalogItemType(QObject):
    value_changed: pyqtSignal(float) = pyqtSignal(float)

    def __init__(self, name: str = 'Аналоговый вход', parent=None):
        super().__init__(parent=parent)
        self._value: float = 0.0
        self.timestamp: datetime = datetime.now()
        self.eu_range: Range = Range(0, 1.6)
        self.instrument_range: Range = Range(4000, 20000)
        self.engineering_units: str = 'МПа'
        self.definition: str = name
        self.value_precision: int = 3

    def get_value(self) -> float:
        return self._value

    @pyqtSlot(float)
    def set_value(self, value: float):
        eu_r = self.eu_range.high - self.eu_range.low
        i_r = self.instrument_range.high - self.instrument_range.low
        if i_r == 0:
            logging.error(f'Диапазон {self.definition} равен 0')
            return
        value = (value - self.instrument_range.low) * eu_r / i_r + self.eu_range.low
        value = round(value, self.value_precision)
        if value != self._value:
            self._value = value
            self.timestamp = datetime.now()
            self.value_changed.emit(value)


class TwoStateDiscreteType(QObject):
    value_changed = pyqtSignal(bool)
    clicked = pyqtSignal()

    def __init__(self, name: str = 'Дискретный вход', parent=None):
        super().__init__(parent=parent)
        self.description: str = name
        self._value: bool = False
        self.false_state: str = 'Откл.'
        self.true_state: str = 'Вкл.'

    def get_value(self) -> bool:
        return self._value

    @pyqtSlot(bool)
    def set_value(self, value: bool):
        if self._value == value: return
        self._value = value
        if value:
            self.clicked.emit()
        self.value_changed.emit(value)

