import pyqtgraph as pg
from opc.server import Server
from typing import Dict, List
from datetime import datetime
from PyQt5.QtCore import pyqtSlot


# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


class Plot(pg.PlotWidget):
    def __init__(self, server: Server, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(300)
        self.manometer = server.manometer
        self.graph: Dict = {}
        self.data: Dict[str, List[float]] = {}
        color = (
            (250, 0, 0),
            (0, 250, 0),
            (0, 250, 250),
            (250, 250, 0),
            (250, 0, 250),
        )

        for i, key in enumerate(self.manometer.keys()):
            graph = self.plot(name=self.manometer[key].name, pen=color[i])
            self.graph[key] = graph
            self.data[key] = []
            graph.setData(x=[], y=[])
        self.data['time'] = []

        self.plotItem.setTitle('График')
        self.plotItem.showGrid(True, True, 0.5)
        self.plotItem.addLegend(offset=(-30, 30))
        self.plotItem.setLabel('bottom', 'Время, с')
        self.plotItem.setLabel('left', 'Давление, МПа')

        self.max_size = 0
        self.t1: datetime = datetime.now()
        self.t2: datetime = self.t1
        self.dt: float = 0
        self.auto_update: bool = False
        server.worker.updated.connect(self.on_server_update)


    def show_graph(self, keys):
        legend = self.plotItem.legend
        for _, label in legend.items[:]:
            legend.removeItem(label.text)
        self.clear()
        self.plotItem.legend.items = []
        for key in self.graph.keys():
            if key in keys:
                self.addItem(self.graph[key])
        self.reset()

    def reset(self):
        self.data['time'] = []
        for key in self.graph.keys():
            self.data[key] = []
            self.graph[key].setData(x=[], y=[])

    @pyqtSlot()
    def start(self):
        self.t1 = datetime.now()
        self.update()

    def start_auto(self):
        self.auto_update = True
        self.start()

    @pyqtSlot()
    def stop(self):
        self.auto_update = False

    @pyqtSlot()
    def update(self):
        self.t2 = datetime.now()
        self.dt = (self.t2 - self.t1).total_seconds()

        time = self.data['time']
        time.append(self.dt)
        time = time[-self.max_size:]
        self.data['time'] = time

        for key in self.manometer.keys():
            manometer = self.manometer[key]
            data = self.data[key]
            data.append(manometer.get_value())
            data = data[-self.max_size:]
            self.data[key] = data
            self.graph[key].setData(x=time, y=data)

    @pyqtSlot()
    def on_server_update(self):
        if self.auto_update:
            self.update()
