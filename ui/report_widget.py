from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrintPreviewWidget
from ui.menu import Menu


class ReportWidget(QWidget):
    up = pyqtSignal()
    down = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.preview = QPrintPreviewWidget()
        self.preview.fitToWidth()
        self.vbox.addWidget(self.preview)
        self.menu = Menu('', show_caption=False)
        self.print = self.menu.add_button('Печать')
        self.passport = self.menu.add_button('Передать даннные в электронный паспорт локомотива')
        self.exit = self.menu.add_button('Вернуться в главное меню')
        self.vbox.addWidget(self.menu)
        self.menu.setFixedHeight(140)
        self.menu.vbox.setContentsMargins(0, 0, 0, 0)

    def event(self, event):
        if not self.isVisible():return QWidget.event(self, event)
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Up:
                self.up.emit()
            elif event.key() == Qt.Key_Down:
                self.down.emit()
        return QWidget.event(self, event)
