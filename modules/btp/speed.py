from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller
p = None


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

        self.setInitialState(self.start)
        self.start.addTransition(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.enter)
        # self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, )


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.button_enable('back')
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
        if tc1 >= 0.56 and tc2 >= 0.56 or t >= 8:
            self.done.emit()


class Ok(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Нажмите и удерживайте кнопку "ОК".</p>'
                     f'<p>Давление в ТЦ1  и ТЦ2 должно уменьшаться.</p>')


class OkMeasure(QState):
    def onEntry(self, event: QEvent) -> None:
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        res1 = 'норма' if tc1 < 0.5 else '(не норма)'
        res2 = 'норма' if tc2 < 0.5 else '(не норма)'
        ctrl.btp.sped_ok = [res1, res2]
        ctrl.setText(f'<p>Давление в ТЦ1  и ТЦ2 должно уменьшаться.</p>'
                     f'<p>Давление в ТЦ1 {tc1} МПа {res1}</p>'
                     f'<p>Давление в ТЦ2 {tc2} МПа {res2}</p>'
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
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст')
        ctrl.button_enable('back')
        data = ctrl.btp.fill_time
        tc1 = data.time_as_text(0)
        tc2 = data.time_as_text(1)
        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времени наполнения ТЦ при управлении'
                     f' краном вспомогательного тормоза (КВТ)</caption>'
                     f'<tr><th>Наименование</th><th>Норма, МПа</th><th>ТЦ1 факт, с</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время наполнения ТЦ при управлении КВТ<br>(с 0 до 0,35 МПа)</td><td>не более 4 с</td>'
                     f'<td align="center">{tc1}</td><td align="center">{tc2}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
        if data.success():
            ctrl.menu.current_menu.current_button.set_success()
        else:
            ctrl.menu.current_menu.current_button.set_fail()
