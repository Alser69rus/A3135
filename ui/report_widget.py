from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent, QFont
from PyQt5.QtGui import QPdfWriter, QPagedPaintDevice
from PyQt5.QtPrintSupport import QPrintPreviewWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget, QVBoxLayout

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
        self.passport.clicked.connect(self.connect_passport)
        self.print.clicked.connect(self.preview.print)
        self.on_preview = None
        self.preview.paintRequested.connect(self.on_paint_request)

    def event(self, event):
        if not self.isVisible(): return QWidget.event(self, event)
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Up:
                self.up.emit()
            elif event.key() == Qt.Key_Down:
                self.down.emit()
        return QWidget.event(self, event)

    def connect_passport(self):
        dialog = QMessageBox()
        dialog.setWindowTitle('Ошибка соединения')
        dialog.setText('Ошибка соединения с электронным паспортом')
        dialog.setFont(QFont('Segoi ui', 14))
        dialog.exec()

    def create_report(self, dev_type: str, dev_num, date):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        today = datetime.today()
        num = self.get_num(settings, today)
        path = self.get_path(settings, dev_type, today)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self.save_new_report_date(settings, today)
        self.save_new_report_num(settings, num)
        file = self.get_file_name(dev_type, num, today, dev_num, date)
        self.save_pdf(path / file)
        self.preview.updatePreview()

    def get_num(self, settings: QSettings, today) -> int:
        last_date = settings.value('protocol/date', '01.01.2019')
        num = settings.value('protocol/num', 0, int)
        month = int(str(last_date).split('.')[1])
        if month != today.month:
            num = 0
        num += 1
        return num

    def get_path(self, settings: QSettings, dev_type: str, today):
        protocol_path = Path(settings.value('protocol/path', 'c:\\протоколы\\'))
        protocol_path = protocol_path / f'{today.strftime("%Y-%m")}' / f'{dev_type}'
        return protocol_path

    def get_file_name(self, dev_type, report_num, today, dev_num, date) -> str:
        return f'N {report_num} от {today.strftime("%d-%m-%Y")} {dev_type} завN' \
               f' {dev_num} дата изг. {date}.pdf'

    def save_pdf(self, file):
        wr = QPdfWriter(str(file))
        wr.setResolution(300)
        wr.newPage()
        wr.setPageSize(QPagedPaintDevice.A4)
        self.on_paint_request(wr)

    def save_new_report_num(self, settings: QSettings, num: int):
        settings.setValue('protocol/num', num)

    def save_new_report_date(self, settings: QSettings, date):
        settings.setValue('protocol/date', date.strftime('%d.%m.%Y'))

    def on_paint_request(self, printer):
        if not (self.on_preview is None):
            self.on_preview(printer)
