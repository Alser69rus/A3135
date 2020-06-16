from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller
p = None


class Filling(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Время наполненя ТЦ'].clicked, self)

        self.start = Start(self)
        self.pim = common.Pim(self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.ppm = common.Ppm(self)
        self.ku_215 = common.KU215(self)
        self.enter = common.Enter(state='КУ', parent=self)
        self.handle_position_four = HandlePositionFour(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.handle_position_four)
        self.handle_position_four.addTransition(ctrl.server_updated, self.handle_position_four)
        self.handle_position_four.addTransition(self.handle_position_four.done, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)
        self.show_result.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.button_enable('back')
        ctrl.btp.fill_time.tc = [0.0, 0.0]
        ctrl.menu.current_menu.current_button.set_normal()


class HandlePositionFour(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Переведите ручку КУ 215 в четвертое положение за один прием.')
        if ctrl.manometer['p im'].get_value() > 0.005:
            ctrl.graph.start()
            ctrl.btp.fill_time.start()
            self.done.emit()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        if tc1 >= 0.35:
            ctrl.btp.fill_time.stop(0)
        if tc2 >= 0.35:
            ctrl.btp.fill_time.stop(1)

        if tc1 >= 0.35 and tc2 >= 0.35 or t > 6:
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
