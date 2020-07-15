from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller
from modules.keb.common import SetPtc, PreparePressure


class Junctions(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)

        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КЭБ 208']
        parent.menu.addTransition(menu.button['Герметичность соединений'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = PreparePressure(self)
        self.set_ptc = SetPtc(self)
        self.check_junctions = CheckJunctions(self)
        self.junctions_success = JunctionsSuccess(self)
        self.junctions_fail = JunctionsFail(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.set_ptc)
        self.set_ptc.addTransition(self.set_ptc.finished, self.check_junctions)
        self.check_junctions.addTransition(ctrl.button['yes'].clicked, self.junctions_success)
        self.check_junctions.addTransition(ctrl.button['no'].clicked, self.junctions_fail)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.keb.junctions.reset()


class CheckJunctions(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_button('back yes no')
        ctrl.setText('<p>Обмыльте мыльным раствором места соединений и атмосферное отверстие в корпусе КЭБ 208.</p>'
                     '<p>Норма: пропуск воздуха не допускается.</p>'
                     '<p><br>Если это обеспечивается - нажмите "ДА" (норма).<br>'
                     'В противном случае нажмите "НЕТ" (не норма).</p>')


class JunctionsSuccess(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.success()
        ctrl.keb.junctions.success()


class JunctionsFail(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.fail()
        ctrl.keb.junctions.fail()
