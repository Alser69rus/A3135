from PyQt5.QtCore import QState, QFinalState, QEvent, QSettings, Qt
from PyQt5.QtGui import QPageLayout, QPageSize, QPainter, QColor, QFont, QPen, QBrush

from controller.controller import Controller

ctrl: Controller


class Ending(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.air = Air(self)
        self.ku_215_on = KU215On(self)
        self.breaking = Breaking(self)
        self.ku_215_off = KU215Off(self)
        self.enter = Enter(self)
        self.disconnect_bto = DisconnectBTO(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.air)
        self.air.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.ku_215_on)
        self.ku_215_on.addTransition(ctrl.switch['ku 215'].high_value, self.breaking)
        self.breaking.addTransition(ctrl.button['yes'].clicked, self.ku_215_off)
        self.ku_215_off.addTransition(ctrl.switch['ku 215'].low_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, self.disconnect_bto)
        self.disconnect_bto.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст манометры')
        ctrl.button_enable('back')


class Air(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключить пневмотумблер "БТП К СТЕНДУ".</p>'
                     f'<p>Включить тумблер "ВХОД" в положение "КУ"</p>')


class KU215On(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "КУ215".</p>')


class Breaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        ctrl.setText(f'<p>Выполните несколько торможений и отпусков краном 215 до '
                     f'состояния когда ТЦ перестанут наполняться.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class KU215Off(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.setText(f'<p>Выключите тумблер "КУ 215".</p>')


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переключите тумблер "ВХОД" в положение "- 0 -".</p>')


class DisconnectBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        ctrl.setText(f'<p>Отсоедините пневматические рукова и электрические шлейфы от БТО.</p>'
                     f'<p>Снимите КУ 215 с прижима.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class Report(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('отчет')
        ctrl.button_enable('back up down yes')
        ctrl.report.on_preview = self.preview
        ctrl.report.create_report('123', '456')

    def onExit(self, event: QEvent) -> None:
        ctrl.report.on_preview = None

    def preview(self, printer):
        SPACE = 50

        layout = QPageLayout()
        layout.setPageSize(QPageSize(QPageSize.A4))
        layout.setOrientation(QPageLayout.Portrait)
        printer.setPageLayout(layout)
        printer.setResolution(300)
        painter = QPainter()

        painter.begin(printer)
        black = QColor(Qt.black)
        red = QColor(Qt.red)
        pen = QPen(black)
        brush = QBrush(black)
        font = QFont('Segoi ui', 9)
        header_font = QFont('Segoi ui', 12)
        painter.setPen(pen)
        painter.setBrush(brush)

        x, y = 625, 94
        painter.setFont(header_font)
        painter.drawText(x, y, f'Протокол испытания № ')
        painter.end()

    # def preview(self, printer):

    #
    #     painter.begin(printer)
    #     black = QtGui.QColor(QtCore.Qt.black)
    #     red = QtGui.QColor(QtCore.Qt.red)
    #     pen = QtGui.QPen(black)
    #     brush = QtGui.QBrush(black)
    #     font = QtGui.QFont('Segoi ui', 9)
    #     header_font = QtGui.QFont('Segoi ui', 12)
    #     painter.setPen(pen)
    #     painter.setBrush(brush)
    #     protocol_num = self.num
    #     protocol_date = datetime.datetime.today().strftime('%d-%m-%Y')
    #
    #     # Заголовок
    #     x, y = 625, 94
    #     painter.setFont(header_font)
    #     painter.drawText(x, y, f'Протокол испытания № {protocol_num: <3d} от  {protocol_date}')
    #     painter.setFont(font)
    #     # Шапка
    #     x = 156
    #     y += SPACE * 2
    #     painter.drawText(x, y, f'Тип блока управления регулятора: {bu.dev_type}')
    #     y += SPACE
    #     painter.drawText(x, y, f'Зав. № {com.frm_main.auth.num}     Дата изготовления: {com.frm_main.auth.date}')
    #     y += SPACE
    #     painter.drawText(x, y, f'Тепловоз № {com.frm_main.auth.locomotive}     Секция: {com.frm_main.auth.section}')
    #     y += SPACE * 1.5
    #
    #     def print_row(*row):
    #         nonlocal x, y
    #         for i, v in enumerate(row):
    #             painter.drawText(x + w[i], y, v)
    #         y += SPACE
    #
    #     def print_graph(x, y, data, caption=''):
    #         width = 800
    #         height = 300
    #         mx = 15
    #         my = 100
    #         ofx = 40
    #         ofy = 20
    #
    #         pen = QtGui.QPen(black)
    #         brush = QtGui.QBrush(black)
    #         painter.setPen(pen)
    #         painter.setBrush(brush)
    #
    #         points = [QtCore.QPointF(x + mx * it[0] + ofx,
    #                                  y + height - my * it[1] - ofy)
    #                   for it in data]
    #         painter.drawLine(x + ofx,
    #                          y + height - ofy + 10,
    #                          x + ofx,
    #                          y + ofx - 20)
    #
    #         painter.drawLine(x + ofx - 10,
    #                          y + height - ofy,
    #                          x + width - ofx,
    #                          y + height - ofy)
    #
    #         for px in range(0, width - ofx * 2, mx * 5):
    #             painter.drawLine(x + px + ofx,
    #                              y + height - ofy + 5,
    #                              x + ofx + px,
    #                              y + height - ofy - 5)
    #             painter.drawText(x + px + 20,
    #                              y + height + 25,
    #                              f'{px / mx :.0f}')
    #
    #         for py in range(1, 6):
    #             painter.drawLine(x + ofx - 5,
    #                              y + height - ofy - py * my / 2,
    #                              x + ofx + 5,
    #                              y + height - ofy - py * my / 2)
    #             painter.drawText(x - 40,
    #                              y + height - ofy - py * my / 2 + 10,
    #                              f'{py / 2 :3.1f}')
    #
    #         painter.drawText(x + ofx + 40,
    #                          y + ofy + 20,
    #                          'I, А')
    #
    #         painter.drawText(x + width - 20,
    #                          y + height - 10,
    #                          't, с')
    #
    #         painter.drawText(x + ofx + 200,
    #                          y + ofy + 20 + SPACE * 7,
    #                          caption)
    #
    #         pen = QtGui.QPen(red)
    #         painter.setPen(pen)
    #         painter.drawPolyline(*points)
    #         pen = QtGui.QPen(black)
    #         painter.setPen(pen)
    #
    #     # Шапка таблицы
    #     y += SPACE * 1.5
    #     w = [0, 800, 1100, 1600]
    #
    #     if not bu.di_res:
    #         print_row('1. Проверка дискретных входов', 'пропуск')
    #     else:
    #         print_row('1. Проверка дискретных входов')
    #         for it in bu.di_res:
    #             if it[1] > 0:
    #                 res = 'норма'
    #             elif it[1] == 0:
    #                 res = 'пропуск'
    #             else:
    #                 res = 'НЕ НОРМА'
    #             print_row(f'         {it[0]}', res)
    #
    #     if not bu.fi_res:
    #         print_row('2. Проверка частотных входов', 'пропуск')
    #     else:
    #         print_row('2. Проверка частотных входов')
    #         for it in bu.fi_res:
    #             print_row(f'        {it[0]}', it[1])
    #
    #     shim_y = y + SPACE * 4
    #     if not bu.shim_res:
    #         print_row('8. Проверка ШИМ', 'пропуск')
    #     else:
    #
    #         print_row('8. Проверка ШИМ')
    #         print_row(
    #             f'         Минимальный ток, А', f'{bu.shim_res1}', f'факт: {bu.shim_i1:5.3f}', f'норма 0,6-0,9 А')
    #         print_row(
    #             f'         Максимальный ток, А', f'{bu.shim_res2}', f'факт: {bu.shim_i2:5.3f}', f'норма 2,1-2,4')
    #         print_row(f'         Монотонность графика:', f'{bu.shim_res3}')
    #         print_graph(x + 100, y, bu.shim_graph, 'График ШИМ')
    #         y += SPACE * 10
    #     pass_type = ['ЭРЧМ30Т4-01', 'ЭРЧМ30Т4-03']
    #     if not (bu.dev_type in pass_type):
    #         if not bu.ai_res:
    #             print_row('4. Проверка аналоговых входов', 'пропуск')
    #         else:
    #             print_row('4. Проверка аналоговых входов')
    #             for it in bu.ai_res:
    #                 res = 'норма' if it[3] else 'НЕ НОРМА'
    #                 print_row(f'        {it[0]: >15}, мА', f'{res}', f'факт: {it[2]:6.3f}', f'норма: {it[1]}')
    #
    #     pass_type = ['ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-07']
    #     if bu.dev_type in pass_type:
    #         msg = {-1: 'НЕ НОРМА', 0: 'пропуск', 1: 'норма'}
    #         res = [msg[it] for it in [bu.rt_1, bu.rt_2, bu.rt_3]]
    #         if not (bu.rt_1 or bu.rt_2 or bu.rt_3):
    #             print_row('5. Проверка канала АВХ3 -Rt', 'пропуск')
    #         else:
    #             print_row('5. Проверка канала АВХ3 -Rt')
    #             print_row(f'         Контрольная точка 0', f'{res[0]}')
    #             print_row(f'         Контрольная точка 100', f'{res[1]}')
    #             print_row(f'         Контрольная точка max', f'{res[2]}')
    #
    #     if bu.dev_type in ['ЭРЧМ30Т3-06', ]:
    #
    #         if not bu.di_res_r:
    #             print_row('6. Резервные дискретные входы', 'пропуск')
    #         else:
    #             print_row('6. Резервные дискретные входы')
    #             for it in bu.di_res_r:
    #                 if it[1] > 0:
    #                     res = 'норма'
    #                 elif it[1] == 0:
    #                     res = 'пропуск'
    #                 else:
    #                     res = 'НЕ НОРМА'
    #                 print_row(f'         {it[0]}', res)
    #
    #         if not bu.fi_res_r:
    #             print_row('7. Резервный частотный вход', 'пропуск')
    #         else:
    #             print_row('7. Резервный частотный вход')
    #             for it in bu.fi_res_r:
    #                 print_row(f'        {it[0]}', it[1])
    #
    #         if not bu.shim_res_r:
    #             print_row('8. Резервный ШИМ', 'пропуск')
    #         else:
    #
    #             print_row('8. Резервный ШИМ')
    #             print_row(f'         Минимальный ток, А', f'{bu.shim_res1_r}', f'факт: {bu.shim_i1_r:5.3f}',
    #                       f'норма 0,6-0,9 А')
    #             print_row(f'         Максимальный ток, А', f'{bu.shim_res2_r}', f'факт: {bu.shim_i2_r:5.3f}',
    #                       f'норма 2,1-2,4')
    #             print_row(f'         Монотонность графика:', f'{bu.shim_res3_r}')
    #             print_graph(x + 1300, shim_y, bu.shim_graph_r, 'График резервного ШИМ')
    #         painter.setFont(header_font)
    #         y += SPACE * 2
    #         painter.drawText(x, y, 'Испытание провел:')
    #         painter.drawText(x + 312, y, f'{com.frm_main.auth.name1: >50}    {"_" * 20}')
    #
    #         y += SPACE * 2
    #         painter.drawText(x, y, 'Испытание проверил:')
    #         painter.drawText(x + 312, y, f'{com.frm_main.auth.name2: >50}    {"_" * 20}')
    #
    #         painter.end()
