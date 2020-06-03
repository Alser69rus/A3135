from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import logging
from typing import List
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client
from opc.opc import AnalogItemType, TwoStateDiscreteType


class MV110_8AC(QObject):
    updated = pyqtSignal()

    def __init__(self, client: Client, unit: int = 16, parent=None):
        super().__init__(parent=parent)
        self.client = client
        self.unit = unit
        self.description: str = 'Модуль ввода аналоговых сигналов ОВЕН МВ110-224.8АС'
        self.pin: List[AnalogItemType] = [AnalogItemType(f'AI_{i}') for i in range(8)]
        self.timestamp = datetime.now()

    @pyqtSlot()
    def update(self):
        rr = self.client.read_holding_registers(0x100, 8, unit=self.unit)
        if rr.isError():
            logging.warning(f"не удалось прочитать {self.description} с ошибкой {rr}")
            return
        for i in range(8):
            self.pin[i].set_value(rr.registers[i])
        self.timestamp = datetime.now()
        self.updated.emit()


class MV_DI(QObject):
    updated = pyqtSignal()

    def __init__(self,
                 client: Client,
                 unit: int = 16,
                 parent=None):
        super().__init__(parent=parent)
        self.timestamp = datetime.now()
        self.client: Client = client
        self.unit = unit
        self.description: str = 'Модуль дискретного вввода ОВЕН'
        self.pin: List[TwoStateDiscreteType] = []


class MV110_16D(MV_DI):
    def __init__(self,
                 client: Client,
                 unit: int = 16,
                 parent=None):
        super().__init__(client=client, unit=unit, parent=parent)
        self.description: str = 'Модуль дискретного вввода ОВЕН МУ110-224.16Д'
        self.pin: List[TwoStateDiscreteType] = [TwoStateDiscreteType(f'DI_{i}') for i in range(16)]

    @pyqtSlot()
    def update(self):
        rr = self.client.read_holding_registers(0x33, 1, unit=self.unit)
        if rr.isError():
            logging.warning(f'не удалось прочитать {self.description} ошибка {rr}')
            return
        pin = [(rr.registers[0] >> i) & 1 for i in range(16)]
        for i in range(16):
            self.pin[i].value = pin[i]
        self.timestamp = datetime.now()
        self.updated.emit()


class MV110_32DN(MV_DI):
    def __init__(self,
                 client: Client,
                 unit: int = 16,
                 parent=None):
        super().__init__(client=client, unit=unit, parent=parent)
        self.description: str = 'Модуль дискретного вввода ОВЕН МУ110-224.32ДН'
        self.pin: List[TwoStateDiscreteType] = [TwoStateDiscreteType(f'DI_{i}') for i in range(32)]

    @pyqtSlot()
    def update(self):
        rr = self.client.read_holding_registers(0x63, 2, unit=self.unit)
        if rr.isError():
            logging.warning(f'не удалось прочитать {self.description} ошибка {rr}')
            return
        pin1 = [(rr.registers[0] >> i) & 1 for i in range(16)]
        pin2 = [(rr.registers[1] >> i) & 1 for i in range(16)]
        pin = pin1 + pin2
        for i in range(32):
            self.pin[i].value = pin[i]
        self.timestamp = datetime.now()
        self.updated.emit()
