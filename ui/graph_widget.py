import pyqtgraph as pg
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


class Plot(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.plotItem.setTitle('График')
        self.plotItem.showGrid(True, True, 0.5)
        self.plotItem.addLegend(offset=(-30, 30))
        self.plotItem.setLabel('bottom', 'Время, с')
        self.plotItem.setLabel('left', 'Давление, МПа')

        self.ppm = self.plot(name='Р пм', pen=(250, 0, 0))
        self.pim = self.plot(name='Р им', pen=(0, 250, 0))
        self.ptc1 = self.plot(name='Р тц1', pen=(0, 250, 250))
        self.ptc2 = self.plot(name='Р тц2', pen=(250, 250, 0))
        self.pupr = self.plot(name='Р упр рд/сд', pen=(250, 0, 250))
