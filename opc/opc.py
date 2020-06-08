from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List


@dataclass()
class Range:
    low: float = 0.0
    high: float = 1.0


class AnalogItemType(QObject):
    value_changed: pyqtSignal(float) = pyqtSignal(float)

    def __init__(self, name: str = 'Аналоговый вход', parent=None):
        super().__init__(parent=parent)
        self._value: float = 0.0
        self.instrument_value: float = 0.0
        self.timestamp: datetime = datetime.now()
        self.eu_range: Range = Range(0, 1.6)
        self.instrument_range: Range = Range(4000, 20000)
        self.engineering_units: str = 'МПа'
        self.name: str = name
        self.value_precision: int = 3

    def get_value(self) -> float:
        return self._value

    @pyqtSlot(float)
    def set_value(self, value: float):
        self.instrument_value = value
        eu_r = self.eu_range.high - self.eu_range.low
        i_r = self.instrument_range.high - self.instrument_range.low
        if i_r == 0:
            logging.error(f'Диапазон {self.name} равен 0')
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
    high_value = pyqtSignal()
    low_value = pyqtSignal()

    def __init__(self, name: str = 'Дискретный вход', parent=None):
        super().__init__(parent=parent)
        self.name: str = name
        self._value: bool = False
        self.false_state: str = 'Откл.'
        self.true_state: str = 'Вкл.'

    def get_value(self) -> bool:
        return self._value

    def value_as_text(self) -> str:
        return self.true_state if self._value else self.false_state

    @pyqtSlot(bool)
    def set_value(self, value: bool):
        if value:
            self.high_value.emit()
        else:
            self.low_value.emit()
        if self._value == value: return
        self._value = value
        if value:
            self.clicked.emit()
        self.value_changed.emit(value)


class MultiStateDiscreteType(QObject):
    value_changed = pyqtSignal(int)

    def __init__(self, name: str = '', enum_values: List[str] = [], parent=None):
        super().__init__(parent=parent)
        self.name: str = name
        self.enum_values: List[str] = enum_values
        self._value: int = 0

    def value_sa_text(self) -> str:
        return self.enum_values[self._value]

    def get_value(self) -> int:
        return self._value

    @pyqtSlot(int)
    def set_value(self, value: int):
        self._value = value
        self.value_changed.emit(value)


class TwoStateWithNeutralType(MultiStateDiscreteType):
    def __init__(self, name: str = '', enum_values: List[str] = [], parent=None):
        super().__init__(name=name, enum_values=enum_values, parent=parent)
        self._state1: bool = False
        self._state2: bool = False
        self.set_value(0)

    @pyqtSlot(bool)
    def set_state1(self, value: bool):
        self._state1 = value
        self.set_state(self._state1, self._state2)

    @pyqtSlot(bool)
    def set_state2(self, value: bool):
        self._state2 = value
        self.set_state(self._state1, self._state2)

    @pyqtSlot(bool, bool)
    def set_state(self, state1: bool, state2: bool):
        if state1 and not state2:
            self.set_value(1)
        elif state2 and not state1:
            self.set_value(2)
        else:
            self.set_value(0)
