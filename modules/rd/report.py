from typing import Tuple

from PyQt5.QtCore import QState, QEvent, QSettings, Qt
from PyQt5.QtGui import QPageLayout, QPageSize, QPainter, QColor, QFont, QPen, QBrush

from controller.controller import Controller

ctrl: Controller


class Report(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.black = QColor(Qt.black)
        self.red = QColor(Qt.red)
        self.brush = QBrush(self.black)
        self.pen = QPen(self.black, 3.0, Qt.SolidLine)
        self.font = QFont('Segoi ui', 9)
        self.font_b = QFont('Segoi ui', 9, 75)
        self.font_hb = QFont('Segoi ui', 12, 75)
        self.font_h = QFont('Segoi ui', 12)
        self.resolution = 300
        self.painter = None
        self.pos = (0, 0)

        self.addTransition(ctrl.report.exit.clicked, parent.parent().finish)
        self.addTransition(ctrl.button['back'].clicked, parent.parent().finish)

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('отчет')
        ctrl.show_button('back up down yes')
        ctrl.report.on_preview = self.preview
        ctrl.update_report_header()
        ctrl.report.create_report('РД 042', ctrl.report_header.dev_num, ctrl.report_header.date)

    def onExit(self, event: QEvent) -> None:
        ctrl.report.on_preview = None

    def get_painter(self, printer) -> QPainter:
        layout = QPageLayout()
        layout.setPageSize(QPageSize(QPageSize.A4))
        layout.setOrientation(QPageLayout.Portrait)
        printer.setPageLayout(layout)
        printer.setResolution(self.resolution)
        painter = QPainter()
        self.painter = painter
        return painter

    def get_report_num_and_date(self) -> Tuple[int, str]:
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        date = settings.value('protocol/date', '01-01-2019')
        num = settings.value('protocol/num', 0, int)
        return num, date

    def draw_text(self, text: str) -> None:
        x, y = self.mm_to_pixel(*self.pos)
        self.painter.drawText(x, y, text)
        self.pos = self.pos[0], self.pos[1] + 5

    def cell(self, *args, **kwargs):
        painter = self.painter
        font = kwargs.get('font', self.font)
        painter.setFont(font)
        x1, y1 = self.mm_to_pixel(*self.pos)
        row = kwargs.get('height', 1)
        y = self.pos[1] + 5 * row
        x2, y2 = self.mm_to_pixel(200, y)
        w = x2 - x1
        h = y2 - y1
        painter.setPen(QPen(self.black, 3.0, Qt.SolidLine))
        painter.drawRect(x1, y1, w, h)
        col = len(args)
        if col == 1:
            painter.drawText(x1, y1, w, h, Qt.AlignCenter, args[0])
        else:
            tab = (120, 160, 200)
            for i, text in enumerate(args):
                x2, y2 = self.mm_to_pixel(tab[i], y)
                w, h = x2 - x1, y2 - y1
                painter.drawRect(x1, y1, w, h)
                painter.drawText(x1, y1, w, h, Qt.AlignCenter, text)
                x1 = x2
        self.pos = (self.pos[0], y)

    def mm_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        k = self.resolution / 25.4
        return round(x * k), round(y * k)

    def preview(self, printer):
        painter = self.get_painter(printer)
        painter.begin(printer)
        self.header()
        self.table()
        self.bottom()
        painter.end()

    def header(self):
        self.painter.setFont(self.font_hb)
        num, date = self.get_report_num_and_date()
        self.pos = (80, 10)
        self.draw_text(f'Протокол № {num} от {date}')
        self.painter.setFont(self.font_h)
        self.pos = (55, 15)
        self.draw_text(f'испытания реле давления РД 042 заводской № {ctrl.report_header.dev_num}')
        self.pos = (25, 25)
        self.cell('Параметр', 'Норма', 'Факт ТЦ2', font=self.font_b)

    def bottom(self):
        self.painter.setFont(self.font_h)
        self.draw_text('')
        self.draw_text('')
        self.draw_text(f'Испытание провел:    __________________ {ctrl.report_header.name_1}')
        self.draw_text('')
        self.draw_text(f'Испытание проверил:__________________ {ctrl.report_header.name_2}')

    def table(self):

        self.fill()
        self.sensitivity()
        self.empty()
        self.valve()
        self.junctions()

    def fill(self):
        self.cell('Время наполнения ТЦ, с', 'не более 4', f'{ctrl.rd.fill.text()}')

    def sensitivity(self):
        self.cell('Автоматическое поддержание зарядного\n'
                  'давления при утечке (чувствительность), МПа',
                  'не более 0,015',
                  f'{ctrl.rd.sensitivity.text()}',
                  height=2
                  )

    def empty(self):
        self.cell('Время снижения давления в ТЦ, с',
                  'не более 10',
                  f'{ctrl.rd.empty.text()}'
                  )

    def junctions(self):
        self.cell('Плотность мест соединений',
                  '',
                  f'{ctrl.rd.junctions}')

    def valve(self):
        self.cell('Герметичность атмосферного клапана',
                  '',
                  f'{ctrl.rd.valve}')
