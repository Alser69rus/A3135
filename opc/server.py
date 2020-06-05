from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt, QSettings
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client
from opc.owen import MV110_16D, MV110_8AC, MV110_32DN, MV_DI
from typing import Dict
from opc.opc import AnalogItemType, TwoStateDiscreteType, TwoStateWithNeutral

UPDATE_DELAY = 50


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.running: bool = True
        self.skip_update: bool = False
        self.client = Client(method='rtu', port='COM9', timeout=0.05, baudrate=115200, retry_on_empty=True)
        self.ai: MV110_8AC = MV110_8AC(client=self.client, unit=16)
        self.di: MV_DI = MV110_32DN(client=self.client, unit=2)

    @pyqtSlot()
    def do_work(self):
        while self.running:
            t = datetime.now()
            # if not self.skip_update:
            #     self.ai.update()
            #     self.di.update()
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
        self.stop_all.connect(self.worker.stop, Qt.DirectConnection)

        self.manometer: Dict[str, AnalogItemType] = self.get_manometer()
        self.button: Dict[str, TwoStateDiscreteType] = self.get_button()
        self.switch: Dict[str, TwoStateDiscreteType] = self.get_switch()
        self.radio_switch: Dict[str, TwoStateWithNeutral] = self.get_radio_switch()

        self.th.start()

    def get_manometer(self) -> Dict[str, AnalogItemType]:
        result: Dict[str, AnalogItemType] = {}
        ai = [
            ('p pm', 'Р пм', 1.6, self.worker.ai.pin[0]),
            ('p im', 'Р им', 1.0, self.worker.ai.pin[1]),
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
            ('back', 'ВОЗВРАТ', self.worker.di.pin[0]),
            ('up', 'ВВЕРХ', self.worker.di.pin[1]),
            ('down', 'ВНИЗ', self.worker.di.pin[2]),
            ('yes', 'ДА', self.worker.di.pin[3]),
            ('no', 'НЕТ', self.worker.di.pin[4]),
            ('examination', 'ИСПЫТАНИЕ', self.worker.di.pin[5]),
            ('ok', 'ОК', self.worker.di.pin[6]),
            ('auto release', 'АВТ ОТПУСК', self.worker.di.pin[7]),
        ]
        for key, name, button in buttons:
            result[key] = button
            button.name = name
        return result

    def get_switch(self) -> Dict[str, TwoStateDiscreteType]:
        result: Dict[str, TwoStateDiscreteType] = {}
        switches = [
            ('ku 215', 'КУ 215', self.worker.di.pin[8]),
            ('el. braking', 'ЗАМ. ЭЛ. ТОРМ.', self.worker.di.pin[9]),
            ('>60 km/h', '> 60 км/ч', self.worker.di.pin[10]),
            ('rd 042', 'РД 042', self.worker.di.pin[11]),
            ('upr rd 042', 'УПР. РД 042', self.worker.di.pin[12]),
            ('keb 208', 'КЭБ 208', self.worker.di.pin[13]),
            ('red 211', 'РЕД 211.020', self.worker.di.pin[14]),
            ('leak 0,5', 'УТЕЧКА d 1', self.worker.di.pin[15]),
            ('leak 1', 'УТЕЧКА d 0.5', self.worker.di.pin[16]),
        ]
        for key, name, switch in switches:
            result[key] = switch
            switch.name = name
        return result

    def get_radio_switch(self) -> Dict[str, TwoStateWithNeutral]:
        result: Dict[str, TwoStateWithNeutral] = {}
        radio_switch = [
            ('enter', 'ВР - 0 - КУ', ['- 0 -', 'ВР', 'КУ'], [self.worker.di.pin[17], self.worker.di.pin[18]]),
            ('rd-0-keb', 'РД 042 - 0 - КЭБ 208', ['- 0 -', 'РД 042', 'КЭБ 208'],
             [self.worker.di.pin[19], self.worker.di.pin[20]]),
        ]
        for key, name, enum, di in radio_switch:
            radio_switch = TwoStateWithNeutral(name=name, enum_values=enum)
            result[key] = radio_switch
            di[0].value_changed.connect(radio_switch.set_state1)
            di[1].value_changed.connect(radio_switch.set_state2)
        return result
