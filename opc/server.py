from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
import logging
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client

UPDATE_DELAY = 50


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ai: OwenAI8AC = OwenAI8AC(unit=16)
        self.di: OwenDI16D = OwenDI16D(unit=2)
        self.running: bool = True
        self.client = Client(method='rtu', port='COM9', timeout=0.05, baudrate=115200, retry_on_empty=True)

    @pyqtSlot()
    def do_work(self):
        while self.running:
            t = datetime.now()
            # self.ai.update(self.client)
            # self.di.update(self.client)
            t = (datetime.now() - t).total_seconds()
            t = round(UPDATE_DELAY - t * 1000)
            if t > 0:
                self.thread().msleep(t)
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.running = False


class Server(QObject):
    stop_all = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.th: QThread = QThread()
        self.worker: Worker = Worker()
        self.worker.moveToThread(self.th)
        self.th.started.connect(self.worker.do_work)
        self.worker.finished.connect(self.th.quit)
        self.stop_all.connect(self.worker.stop)
        self.worker.finished.connect(self.worker.deleteLater)
        self.th.finished.connect(self.th.deleteLater)

        self.sensor = {'ppm': self.worker.ai.pin[0],
                       'pim': self.worker.ai.pin[1],
                       'ptc1': self.worker.ai.pin[2],
                       'ptc2': self.worker.ai.pin[3],
                       'pupr': self.worker.ai.pin[4], }

        self.th.start()


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

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
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


class OwenAI8AC(QObject):
    updated = pyqtSignal()

    def __init__(self, name: str = 'Модуль ввода аналоговых сигналов ОВЕН МВ110-224.8АС', unit: int = 16, parent=None):
        super().__init__(parent=parent)
        self.unit = unit
        self.description = name
        self.pin: List[AnalogItemType] = [AnalogItemType(f'Датчик давления {i}') for i in range(8)]
        self.timestamp = datetime.now()

    def update(self, client: Client):
        rr = client.read_holding_registers(0x100, 8, unit=self.unit)
        if rr.isError():
            logging.warning(f"не удалось прочитать {self.description} с ошибкой {rr}")
            return
        for i in range(8):
            self.pin[i].value = rr.registers[i]
        self.timestamp = datetime.now()
        self.updated.emit()


class TwoStateDiscreteType(QObject):
    value_changed = pyqtSignal(bool)
    clicked = pyqtSignal()

    def __init__(self, name: str = 'Дискретный вход', parent=None):
        super().__init__(parent=parent)
        self.description: str = name
        self._value: bool = False
        self.false_state: str = 'Откл.'
        self.true_state: str = 'Вкл.'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value: return
        self._value = value
        if value: self.clicked.emit()
        self.value_changed.emit(value)


class OwenDI16D(QObject):
    updated = pyqtSignal()

    def __init__(self, name: str = 'Модуль дискретного вввода ОВЕН МУ110-224.16Д', unit: int = 16, parent=None):
        super().__init__(parent=parent)
        self.unit = unit
        self.description: str = name
        self.pin: List[TwoStateDiscreteType] = [TwoStateDiscreteType(f'Дискретный вход {i}') for i in range(16)]
        self.timestamp = datetime.now()

    def update(self, client: Client):
        rr = client.read_holding_registers(0x33, 1, unit=self.unit)
        if rr.isError():
            logging.warning(f'не удалось прочитать {self.description} ошибка {rr}')
            return
        pin = [(rr.registers[0] >> i) & 1 for i in range(16)]
        for i in range(16):
            self.pin[i].value = pin[i]
        self.timestamp = datetime.now()
        self.updated.emit()
