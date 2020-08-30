from datetime import datetime
from typing import Dict, List

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt, QSettings
from pymodbus.client.sync import ModbusSerialClient as Client

from opc.opc import AnalogItemType, TwoStateDiscreteType, TwoStateWithNeutralType, Range
from opc.owen import MV110_8AC, MV110_32DN, MV_DI

UPDATE_DELAY = 50


class Worker(QObject):
    finished = pyqtSignal()
    updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.running: bool = True
        self.skip_update: bool = False
        self.client = Client(method='rtu', port='COM3', timeout=0.05, baudrate=115200, retry_on_empty=True, retries=5, strict=False)
        self.ai: MV110_8AC = MV110_8AC(client=self.client, unit=1)
        settings = QSettings('manometers.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        manometers = [
            settings.value('ppm', (0, 1.6)),
            settings.value('pim', (0, 1.0)),
            settings.value('ptc1', (0, 1.0)),
            settings.value('ptc2', (0, 1.0)),
            settings.value('pupr', (0, 1.0)),
        ]
        for i, v in enumerate(manometers):
            self.ai.pin[i].eu_range = Range(float(manometers[i][0]), float(manometers[i][1]))

        self.di: MV_DI = MV110_32DN(client=self.client, unit=2)

    @pyqtSlot()
    def do_work(self):
        while self.running:
            t = datetime.now()
            if not self.skip_update:
                t = t
                # self.ai.update()
                # self.di.update()
            t = (datetime.now() - t).total_seconds()
            t = round(UPDATE_DELAY - t * 1000)
            if t > 0:
                self.thread().msleep(t)
            self.updated.emit()
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
        self.stop_all.connect(self.worker.stop, Qt.DirectConnection)

        self.manometer: Dict[str, AnalogItemType] = self.get_manometer()
        self.button: Dict[str, TwoStateDiscreteType] = self.get_button()
        self.switch: Dict[str, TwoStateDiscreteType] = self.get_switch()
        self.switch_with_neutral: Dict[str, TwoStateWithNeutralType] = self.get_switch_with_neutral()

        self.th.start()

    def get_manometer(self) -> Dict[str, AnalogItemType]:
        result: Dict[str, AnalogItemType] = {}
        ai = [
            ('p pm', 'Р пм', 1.0, self.worker.ai.pin[0]),
            ('p tm', 'Р тм', 1.0, self.worker.ai.pin[1]),
            ('p tc1', 'Р тц1', 1.0, self.worker.ai.pin[2]),
            ('p tc2', 'Р тц2', 1.0, self.worker.ai.pin[3]),
            ('p upr', 'Р упр рд/сд', 1.0, self.worker.ai.pin[4]),
        ]
        for key, name, max_value, manometer in ai:
            result[key] = manometer
            manometer.name = name
            manometer.eu_range.high = max_value
        return result

    def get_button(self) -> Dict[str, TwoStateDiscreteType]:
        result: Dict[str, TwoStateDiscreteType] = {}
        buttons = [
            ('back', 'ВОЗВРАТ', self.worker.di.pin[15]),
            ('up', 'ВВЕРХ', self.worker.di.pin[16]),
            ('down', 'ВНИЗ', self.worker.di.pin[17]),
            ('yes', 'ДА', self.worker.di.pin[18]),
            ('no', 'НЕТ', self.worker.di.pin[19]),
        ]
        for key, name, button in buttons:
            result[key] = button
            button.name = name
        return result

    def get_switch(self) -> Dict[str, TwoStateDiscreteType]:
        result: Dict[str, TwoStateDiscreteType] = {}
        switches = [
            ('rd 042', 'РД 042', self.worker.di.pin[2]),
            ('upr rd 042', 'УПР. РД 042', self.worker.di.pin[3]),
            ('sd', 'СД', self.worker.di.pin[4]),
            ('keb 208', 'КЭБ 208', self.worker.di.pin[5]),
            ('red 211', 'РЕД 211.020', self.worker.di.pin[6]),
            ('ku 215', 'КУ 215', self.worker.di.pin[7]),
            ('tc 820', 'ТЦ2 8 л - 20 л', self.worker.di.pin[10]),
            ('leak 1', 'УТЕЧКА d 1', self.worker.di.pin[11]),
            ('gap', 'РАЗРЫВ', self.worker.di.pin[12]),
            ('leak 0,5', 'УТЕЧКА d 0.5', self.worker.di.pin[13]),
            ('kp 106', 'КП 106', self.worker.di.pin[14]),
            ('auto', 'АВТ. ОТПУСК', self.worker.di.pin[20]),
            ('zam', 'ЗАМ.', self.worker.di.pin[21]),
            ('edt', 'ЭДТ', self.worker.di.pin[22]),
            ('50-100', '50 В/100 В', self.worker.di.pin[23]),
        ]
        for key, name, switch in switches:
            result[key] = switch
            switch.name = name
        return result

    def get_switch_with_neutral(self) -> Dict[str, TwoStateWithNeutralType]:
        result: Dict[str, TwoStateWithNeutralType] = {}
        radio_switch = [
            ('rd-0-keb', 'РД 042 - 0 - КП 106', ['- 0 -', 'РД 042', 'КП 106'],
             [self.worker.di.pin[8], self.worker.di.pin[9]]),
            ('km', 'КМ', ['- П -', 'О', 'Т'], [self.worker.di.pin[0], self.worker.di.pin[1]]),
        ]
        for key, name, enum, di in radio_switch:
            radio_switch = TwoStateWithNeutralType(name=name, enum_values=enum)
            result[key] = radio_switch
            di[0].updated.connect(radio_switch.set_state1)
            di[1].updated.connect(radio_switch.set_state2)
        return result


def manometer_builder(name: str, limit: float, pin: AnalogItemType) -> AnalogItemType:
    pin.name = name
    pin.eu_range.high = limit
    return pin


def button_builder(name: str, pin: TwoStateDiscreteType) -> TwoStateDiscreteType:
    pin.name = name
    return pin


def switch_builder(name: str, pin: TwoStateDiscreteType) -> TwoStateDiscreteType:
    pin.name = name
    return pin


def multi_switch_builder(name: str, state: List[str], pin: List[TwoStateDiscreteType]) -> TwoStateWithNeutralType:
    switch = TwoStateWithNeutralType(name=name, enum_values=state)
    pin[0].updated.connect(switch.set_state1)
    pin[1].updated.connect(switch.set_state2)
    return switch
