from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


class Valve(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КУ 215']
        parent.menu.addTransition(menu.button['Герметичность клапана'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_4 = common.pressure_4(self)
        self.check_valve = CheckValve(self)
        self.valve_fail = ValveFail(self)
        self.valve_success = ValveSuccess(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_4)
        self.pressure_4.addTransition(ctrl.server_updated, self.pressure_4)
        self.pressure_4.addTransition(ctrl.button['yes'].clicked, self.check_valve)
        self.check_valve.addTransition(ctrl.button['yes'].clicked, self.valve_success)
        self.check_valve.addTransition(ctrl.button['no'].clicked, self.valve_fail)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.graph.show_graph('p im')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.valve.reset()


class CheckValve(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes no')
        ctrl.setText('<p>Закройте клапан на атмосферной трубе, отходящей от плиты прижима КУ 215.</p>'
                     '<p>Обмыльте мыльным раствором дренажный отросток крана на атмосферной трубе, '
                     'отходящей от плиты прижима КУ 215.</p>'
                     '<p>Норма: пропуск воздуха не допускается.</p>'
                     '<p>Если это обеспечивается - нажмите "ДА",<br>'
                     '<br>В противном случае нажмите "НЕТ".</p>')


class ValveFail(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.fail()
        ctrl.ku.valve.fail()


class ValveSuccess(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        ctrl.ku.valve.success()
