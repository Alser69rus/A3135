from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller


class KvtBreaking(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['торможение КВТ'].clicked, self)

        self.start = Start(self)
        self.pim = common.Pim(self)
        self.check_1 = Check(stage=0, parent=self)
        self.check_2 = Check(stage=1, parent=self)
        self.check_3 = Check(stage=2, parent=self)
        self.check_4 = Check(stage=3, parent=self)
        self.check_5 = Check(stage=4, parent=self)
        self.check_6 = Check(stage=5, parent=self)
        self.check_7 = Check(stage=6, parent=self)
        self.check_8 = Check(stage=7, parent=self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.check_1)
        self.check_1.addTransition(self.check_1.finished, self.check_2)
        self.check_2.addTransition(self.check_2.finished, self.check_3)
        self.check_3.addTransition(self.check_3.finished, self.check_4)
        self.check_4.addTransition(self.check_4.finished, self.check_5)
        self.check_5.addTransition(self.check_5.finished, self.check_6)
        self.check_6.addTransition(self.check_6.finished, self.check_7)
        self.check_7.addTransition(self.check_7.finished, self.check_8)
        self.check_8.addTransition(self.check_8.finished, self.show_result)
        self.show_result.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.graph.reset()
        ctrl.button_enable('back')

        ctrl.btp.kvt_breaking.tc1 = [-1.0] * 8
        ctrl.btp.kvt_breaking.tc2 = [-1.0] * 8
        ctrl.menu.current_menu.current_button.set_normal()


class SaveResult(QFinalState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        self.stage = stage

    def onEntry(self, event: QEvent) -> None:
        ctrl.btp.kvt_breaking.tc1[self.stage] = ctrl.manometer['p tc1'].get_value()
        ctrl.btp.kvt_breaking.tc2[self.stage] = ctrl.manometer['p tc2'].get_value()


class Check(QState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        common = Common(controller=ctrl)
        self.ppm = common.Ppm(self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.ku_215 = common.KU215(self)
        self.enter = common.Enter(state='КУ', parent=self)
        self.handle_position = common.HandlePosition(stage=stage, parent=self)
        self.check_handle_position = common.CheckHandlePosition(stage=stage, data=ctrl.btp.kvt_breaking, parent=self)
        self.pressure_stabilization = common.PressureStabilization(self)
        self.save_result = SaveResult(stage=stage, parent=self)

        self.setInitialState(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.handle_position)
        self.handle_position.addTransition(self.check_handle_position)
        self.check_handle_position.addTransition(ctrl.server_updated, self.check_handle_position)
        self.check_handle_position.addTransition(self.check_handle_position.done, self.pressure_stabilization)
        self.pressure_stabilization.addTransition(ctrl.server_updated, self.pressure_stabilization)
        self.pressure_stabilization.addTransition(self.pressure_stabilization.done, self.save_result)


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.show_panel('текст')
        text = f'<p><table border="2" cellpadding="4" >' \
               f'<caption>Проверка ступеней торможения и отпуска при управлении ' \
               f'краном вспомогательного тормоза (КВТ)</caption>' \
               f'<tr><th>Ступень</th><th>Норма, МПа</th><th>ТЦ1 факт, МПа</th><th>ТЦ2 факт, МПа</th></tr>' \
               f'<tr><th colspan="4">Торможение</th></tr>'

        for i in range(4):
            text += self.get_row(i)
        text += f'<tr><th colspan="4">Отпуск</th></tr>'
        for i in range(4, 8):
            text += self.get_row(i)

        text += f'</table></p>'
        text += f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>'
        ctrl.setText(text)

        if ctrl.btp.kvt_breaking.success():
            ctrl.menu.current_menu.current_button.set_success()
        else:
            ctrl.menu.current_menu.current_button.set_fail()

    def get_row(self, row: int):
        data = ctrl.btp.kvt_breaking
        stage = data.stage[row]
        rang = data.range_as_text(row)
        tc1 = data.tc1_as_text(row)
        tc2 = data.tc2_as_text(row)
        return f'<tr><td>   {stage}  </td><td>   {rang}   </td>' \
               f'<td align="center">   {tc1}   </td><td align="center">   {tc2}   </td></tr>'
