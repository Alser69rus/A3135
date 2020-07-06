from typing import Tuple

from PyQt5.QtCore import QState, QEvent, QSettings, Qt
from PyQt5.QtGui import QPageLayout, QPageSize, QPainter, QColor, QFont, QPen, QBrush

from controller.controller import Controller

ctrl: Controller


class Report(QState):
    def __init__(self, controller: Controller, parent=None):
        super().__init__(parent=parent)
        global ctrl
        ctrl = controller
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

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('отчет')
        ctrl.button_enable('back up down yes')
        ctrl.report.on_preview = self.preview
        ctrl.update_report_header()
        ctrl.report.create_report(ctrl.report_header.dev_num, ctrl.report_header.date)

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
        self.pos = (35, 15)
        self.draw_text(f'испытания блока тормозных приборов 020 для тепловозов ТЭП70')
        self.draw_text(f'Заводской № {ctrl.report_header.dev_num}             '
                       f'Дата изготовления: {ctrl.report_header.date}')
        self.draw_text(f'Локомотив: {ctrl.report_header.locomotive}                '
                       f'Секция: {ctrl.report_header.section}')

    def bottom(self):
        self.painter.setFont(self.font_h)
        self.draw_text('')
        self.draw_text('')
        self.draw_text(f'Испытание провел:    __________________ {ctrl.report_header.name_1}')
        self.draw_text('')
        self.draw_text(f'Испытание проверил:__________________ {ctrl.report_header.name_2}')

    def table(self):
        self.pos = (25, 30)
        self.auto_break()
        self.kvt_break()
        self.fill()
        self.tightness()
        self.empty()
        self.substitution()
        self.speed()

    def substitution(self):
        self.cell('Проверка работы БТП при замещении электрического тормоза', font=self.font_b)
        self.cell('Время наполнения ТС, с\n(с 0 до 0,16 МПА)',
                  'не более 4c',
                  f'{ctrl.btp.substitution.time_as_text(0)}',
                  f'{ctrl.btp.substitution.time_as_text(1)}'
                  , height=2)

    def speed(self):
        self.cell('Проверка работы БТП при движении локомотива на повышенных скоростях', font=self.font_b)
        self.cell('Время наполнения ТЦ, с\n(с 0 до 0,56 МПа)',
                  'не более 4 с',
                  f'{ctrl.btp.speed_fill.time_as_text(0)}',
                  f'{ctrl.btp.speed_fill.time_as_text(1)}',
                  height=2)
        self.cell('Время снижения давления в ТЦ, с\n(с max до 0 МПа)',
                  'не более 4 с',
                  f'{ctrl.btp.speed_empty.time_as_text(0)}',
                  f'{ctrl.btp.speed_empty.time_as_text(1)}',
                  height=2)
        self.cell('Проверка проходимости канала к\n отпускному клапвну',
                  '',
                  f'{ctrl.btp.sped_ok[0]}',
                  f'{ctrl.btp.sped_ok[1]}',
                  height=2)

    def fill(self):
        self.cell('Время наполнения ТЦ \nпри управлении КВТ, с\n(с 0 до 0,35 МПа)',
                  'не более 4 с',
                  f'{ctrl.btp.fill_time.time_as_text(0)}',
                  f'{ctrl.btp.fill_time.time_as_text(1)}',
                  height=3)

    def tightness(self):
        self.cell('Герметичность мест соединений', '', f'{ctrl.btp.tightness}')

    def empty(self):
        self.cell('Время снижения давления в ТЦ\nпри управлении КВТ, с\n(с 0,35 до 0,005 МПа)',
                  'не более 13 с',
                  f'{ctrl.btp.empty_time.time_as_text(0)}',
                  f'{ctrl.btp.empty_time.time_as_text(1)}',
                  height=3)

    def auto_break(self):
        self.cell(f'Проверка ступенчатого торможения и отпуска при действии автоматического тормоза', font=self.font_b)
        self.cell('Ступень ВР', 'Норма, МПа', 'ТЦ1, МПа', 'ТЦ2, МПа')
        self.cell('Торможение')
        for i in range(4):
            self.cell(f'{ctrl.btp.auto_breaking.position_as_text(i)}',
                      f'{ctrl.btp.auto_breaking.range_as_text(i)}',
                      f'{ctrl.btp.auto_breaking.tc_as_text(0, i)}',
                      f'{ctrl.btp.auto_breaking.tc_as_text(1, i)}')
        self.cell('Отпуск')
        for i in range(4, 8):
            self.cell(f'{ctrl.btp.auto_breaking.position_as_text(i)}',
                      f'{ctrl.btp.auto_breaking.range_as_text(i)}',
                      f'{ctrl.btp.auto_breaking.tc_as_text(0, i)}',
                      f'{ctrl.btp.auto_breaking.tc_as_text(1, i)}')

    def kvt_break(self):
        self.cell(f'Проверка ступенчатого торможения и отпуска при управлении краном\nвспомогательного тормоза',
                  font=self.font_b, height=2)
        self.cell('Ступень ВР', 'Норма, МПа', 'ТЦ1, МПа', 'ТЦ2, МПа')
        self.cell('Торможение')
        for i in range(4):
            self.cell(f'{ctrl.btp.kvt_breaking.position_as_text(i)}',
                      f'{ctrl.btp.kvt_breaking.range_as_text(i)}',
                      f'{ctrl.btp.kvt_breaking.tc_as_text(0, i)}',
                      f'{ctrl.btp.kvt_breaking.tc_as_text(1, i)}')
        self.cell('Отпуск')
        for i in range(4, 8):
            self.cell(f'{ctrl.btp.kvt_breaking.position_as_text(i)}',
                      f'{ctrl.btp.kvt_breaking.range_as_text(i)}',
                      f'{ctrl.btp.kvt_breaking.tc_as_text(0, i)}',
                      f'{ctrl.btp.kvt_breaking.tc_as_text(1, i)}')

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
            tab = (90, 120, 160, 200)
            for i, text in enumerate(args):
                x2, y2 = self.mm_to_pixel(tab[i], y)
                w, h = x2 - x1, y2 - y1
                painter.drawRect(x1, y1, w, h)
                painter.drawText(x1, y1, w, h, Qt.AlignCenter, text)
                x1 = x2
        self.pos = (self.pos[0], y)
