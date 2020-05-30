from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client
from opc.owen import DI16D, AI8AC
from typing import Dict
from opc.opc import AnalogItemType, TwoStateDiscreteType

UPDATE_DELAY = 50


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.running: bool = True
        self.client = Client(method='rtu', port='COM9', timeout=0.05, baudrate=115200, retry_on_empty=True)
        self.ai: AI8AC = AI8AC(client=self.client, unit=16)
        self.di: DI16D = DI16D(client=self.client, unit=2)

    @pyqtSlot()
    def do_work(self):
        while self.running:
            t = datetime.now()
            # self.ai.update()
            # self.di.update()
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
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.th.finished.connect(self.th.deleteLater)

        self.ai: Dict[str, AnalogItemType] = {'ppm': self.worker.ai.pin[0],
                                              'pim': self.worker.ai.pin[1],
                                              'ptc1': self.worker.ai.pin[2],
                                              'ptc2': self.worker.ai.pin[3],
                                              'pupr': self.worker.ai.pin[4], }
        self.di: Dict[str, TwoStateDiscreteType] = {'back': self.worker.di.pin[0],
                                                    'up': self.worker.di.pin[1],
                                                    'down': self.worker.di.pin[2],
                                                    'yes': self.worker.di.pin[3],
                                                    'no': self.worker.di.pin[4],
                                                    }

        self.th.start()
