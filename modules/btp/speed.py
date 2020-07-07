from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller


class Speed(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Повышенная скорость'].clicked, self)

        self.start = Start(self)
        self.ppm = common.Ppm(self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.ku_215 = common.KU215(self)
        self.pim = common.Pim(self)
        self.enter = common.Enter(state='- 0 -', parent=self)
        self.speed_on = SpeedOn(self)
        self.measure_fill = MeasureFill(self)
        self.ok = Ok(self)
        self.ok_measure = OkMeasure(self)
        self.speed_off = SpeedOff(self)
        self.measure_empty = MeasureEmpty(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, self.speed_on)
        self.speed_on.addTransition(ctrl.switch['>60 km/h'].high_value, self.measure_fill)
        self.measure_fill.addTransition(ctrl.server_updated, self.measure_fill)
        self.measure_fill.addTransition(self.measure_fill.done, self.ok)
        self.ok.addTransition(ctrl.switch['ok'].high_value, self.ok_measure)
        self.ok_measure.addTransition(ctrl.server_updated, self.ok_measure)
        self.ok_measure.addTransition(ctrl.switch['ok'].low_value, self.speed_off)
        self.speed_off.addTransition(ctrl.switch['>60 km/h'].low_value, self.measure_empty)
        self.measure_empty.addTransition(ctrl.server_updated, self.measure_empty)
        self.measure_empty.addTransition(self.measure_empty.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.show_button('back')
        ctrl.btp.speed_fill.tc = [0.0, 0.0]
        ctrl.btp.speed_empty.tc = [0.0, 0.0]
        ctrl.btp.sped_ok = ['-', '-']
        ctrl.menu.current_menu.current_button.set_normal()


class SpeedOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Включите тумблер "> 60 км/ч". Будет зафиксировано время наполнения ТЦ1 и ТЦ2 '
                     f'до 0,56 МПа. Норма не более 4 с.')

    def onExit(self, event: QEvent) -> None:
        ctrl.btp.speed_fill.start()
        ctrl.graph.start()


class MeasureFill(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        if tc1 >= 0.56:
            ctrl.btp.speed_fill.stop(0)
        if tc2 >= 0.56:
            ctrl.btp.speed_fill.stop(1)
        if tc1 >= 0.56 and tc2 >= 0.56:
            self.done.emit()


class Ok(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Нажмите и удерживайте кнопку "ОК".</p>'
                     f'<p>Давление в ТЦ1  и ТЦ2 должно уменьшаться.</p>')


class OkMeasure(QState):
    def onEntry(self, event: QEvent) -> None:
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        res1 = 'норма' if tc1 < 0.55 else '(не норма)'
        res2 = 'норма' if tc2 < 0.55 else '(не норма)'
        ctrl.btp.sped_ok = [res1, res2]
        ctrl.setText(f'<p>Давление в ТЦ1  и ТЦ2 должно уменьшаться.</p>'
                     f'<p>Давление в ТЦ1: {tc1} МПа<br>результат: {res1}</p>'
                     f'<p>Давление в ТЦ2: {tc2} МПа<br>результат: {res2}</p>'
                     f'<p><br>Для продолжения испытания отпустите кнопку "ОК".</p>')


class SpeedOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Выключите тумблер "> 60 км/ч". Будет зафиксировано время снижения давления ТЦ1 и ТЦ2. '
                     f'Норма не более 4 с.')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.reset()
        ctrl.graph.start()
        ctrl.btp.speed_empty.start(0)
        ctrl.btp.speed_empty.start(1)


class MeasureEmpty(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        if tc1 <= 0.005:
            ctrl.btp.speed_empty.stop(0)
        if tc2 <= 0.005:
            ctrl.btp.speed_empty.stop(1)
        if tc1 <= 0.005 and tc2 <= 0.005:
            self.done.emit()


class ShowResult(QState):
    text = ''

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст')
        ctrl.show_button('back')
        data_fill = ctrl.btp.speed_fill
        data_empty = ctrl.btp.speed_empty
        data_ok = ctrl.btp.sped_ok
        self.table_begin()
        self.caption('Проверка работы БТО при движении на повышенных скоростях')
        self.header('Наименование', 'Норма', 'ТЦ1 факт, с', 'ТЦ2 факт, с')
        self.row(f'Время наполнения ТЦ1 и ТЦ2<br>с 0 до 0,56 МПа', 'не более 4 с',
                 f'{data_fill.time_as_text(0)}', f'{data_fill.time_as_text(1)}')
        self.row('Время снижения давления в ТЦ1 и ТЦ2<br>с max до 0', 'не более 13 с',
                 f'{data_empty.time_as_text(0)}', f'{data_empty.time_as_text(1)}')
        self.row('Проверка проходимости канала к отпускному клапану', '', f'{data_ok[0]}', f'{data_ok[1]}')
        self.table_end()
        self.text += '<p><br>Для выхода в меню нажмите "ВОЗВРАТ".</p>'
        ctrl.setText(self.text)

        res = all(s == 'норма' for s in data_ok)
        if data_fill.success() and data_empty.success() and res:
            ctrl.menu.current_menu.current_button.set_success()
        else:
            ctrl.menu.current_menu.current_button.set_fail()

    def table_begin(self):
        self.text += f'<p><table border="2" cellpadding="4">'

    def table_end(self):
        self.text += f'</table></p>'

    def caption(self, caption: str):
        self.text += f'<caption>{caption}</caption>'

    def header(self, *args):
        self.text += '<tr>'
        for arg in args:
            self.text += '<th>'
            self.text += arg
            self.text += '</th>'
        self.text += '</tr>'

    def row(self, *args) -> str:
        self.text += '<tr>'
        for arg in args:
            self.text += '<td align="center">'
            self.text += arg
            self.text += '</td>'
        self.text += '</tr>'
