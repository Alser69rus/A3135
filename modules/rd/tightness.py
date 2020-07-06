from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller


class Tightness(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Герметичность'].clicked, self)

        self.start = Start(self)
        self.ppm = common.Ppm(self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.ku_215 = common.KU215(self)
        self.enter = common.Enter(state='КУ', parent=self)
        self.handle_position_four = common.HandlePositionFour(self)
        self.check = Check(self)
        self.yes = Yes(self)
        self.no = No(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.handle_position_four)
        self.handle_position_four.addTransition(ctrl.server_updated, self.handle_position_four)
        self.handle_position_four.addTransition(self.handle_position_four.done, self.check)
        self.check.addTransition(ctrl.button['yes'].clicked, self.yes)
        self.check.addTransition(ctrl.button['no'].clicked, self.no)
        self.yes.addTransition(self.finish)
        self.no.addTransition(self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back yes no')
        ctrl.menu.current_menu.current_button.set_normal()
        ctrl.btp.tightness = '-'


class Check(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes no')
        ctrl.setText(f'<p>Обмылить мыльным раствором места соединений сборочных удиниц и деталей БТО.</p>'
                     f'<p>Норма: пропуск воздуха не допускается.</p>'
                     f'<p><br>Если это обеспечивается нажмите "ДА" (норма),<br>'
                     f'в противном случае нажмите "НЕТ" (не норма).</p>')


class Yes(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.current_menu.current_button.set_success()
        ctrl.btp.tightness = 'норма'


class No(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.current_menu.current_button.set_fail()
        ctrl.btp.tightness = 'не норма'
