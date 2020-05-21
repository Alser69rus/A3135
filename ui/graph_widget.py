import pyqtgraph as pg
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


class Plot(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.plotItem.setTitle('График')
        self.plotItem.showGrid(True,True,0.5)
        self.plotItem.addLegend(offset=(-30,30))
        self.plotItem.setLabel('bottom','Время','сек')
        self.plotItem.setLabel('left','Давление','МПа')


