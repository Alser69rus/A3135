from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.ku.common import Common
from modules.ku.report import Report

ctrl: Controller


class End(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КУ 215']
        parent.menu.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.pressure_0 = common.pressure_0(self)
        self.ku = Ku(self)
        self.uninstall = Uninstall(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_0)
        self.pressure_0.addTransition(ctrl.server_updated, self.pressure_0)
        self.pressure_0.addTransition(ctrl.button['yes'].clicked, self.ku)
        self.ku.addTransition(ctrl.switch['ku 215'].low_value, self.uninstall)
        self.uninstall.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')


class Ku(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "КУ 215".')


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('<p>Снимите КУ 215 с прижима.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
