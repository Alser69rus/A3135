from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import logging
from typing import List
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client
from lib.opc.io import DInput


class MV110(QObject):
    updated = pyqtSignal()

    def __init__(self, parent, unit: int = 16):
        super().__init__(parent=parent)

        self.timestamp = datetime.now()
        self.client: Client = parent.client
        self.unit = unit
        self.name: str = 'Модуль дискретного вввода ОВЕН'
        self.pin: List[DInput] = []


class MV11016D(MV110):
    def __init__(self, parent, unit: int = 16):
        super().__init__(parent=parent, unit=unit)
        self.name: str = 'Модуль дискретного вввода ОВЕН МУ110-224.16Д'
        self.pin: List[DInput] = [DInput()] * 16

    @pyqtSlot()
    def update(self):
        rr = self.client.read_holding_registers(0x33, 1, unit=self.unit)
        if rr.isError():
            logging.warning(f'не удалось прочитать {self.name} ошибка {rr}')
            return
        pin = [(rr.registers[0] >> i) & 1 for i in range(16)]
        for i in range(16):
            self.pin[i].set_value(pin[i])
        self.timestamp = datetime.now()
        self.updated.emit()


class MV11032DN(MV110):
    def __init__(self, parent, unit: int = 16):
        super().__init__(parent=parent, unit=unit)
        self.name: str = 'Модуль дискретного вввода ОВЕН МУ110-224.32ДН'
        self.pin: List[DInput] = [DInput()] * 32

    @pyqtSlot()
    def update(self):
        rr = self.client.read_holding_registers(0x63, 2, unit=self.unit)
        if rr.isError():
            logging.warning(f'не удалось прочитать {self.name} ошибка {rr}')
            return
        pin1 = [(rr.registers[1] >> i) & 1 for i in range(16)]
        pin2 = [(rr.registers[0] >> i) & 1 for i in range(16)]
        pin = pin1 + pin2
        for i in range(32):
            self.pin[i].set_value(pin[i])
        self.timestamp = datetime.now()
        self.updated.emit()
