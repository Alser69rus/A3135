from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


class Junctions(QState):
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
        parent.menu.addTransition(menu.button['Герметичность соединений'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_4 = common.pressure_4(self)
        self.check_junctions = CheckJunctions(self)
        self.junctions_fail = JunctionsFail(self)
        self.junctions_success = JunctionsSuccess(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_4)
        self.pressure_4.addTransition(ctrl.server_updated, self.pressure_4)
        self.pressure_4.addTransition(ctrl.button['yes'].clicked, self.check_junctions)
        self.check_junctions.addTransition(ctrl.button['yes'].clicked, self.junctions_success)
        self.check_junctions.addTransition(ctrl.button['no'].clicked, self.junctions_fail)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.graph.show_graph('p im')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.junctions.reset()


class CheckJunctions(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes no')
        ctrl.setText('<p>Обмыльте мыльным раствором места соединений сборочных единиц и деталей КУ 215.</p>'
                     '<p>Норма: пропуск воздуха не допускается.</p>'
                     '<p>Если это обеспечивается - нажмите "ДА",<br>'
                     '<br>В противном случае нажмите "НЕТ".</p>')


class JunctionsFail(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.fail()
        ctrl.ku.junctions.fail()


class JunctionsSuccess(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        ctrl.ku.junctions.success()
