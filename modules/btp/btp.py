from PyQt5.QtCore import QState, QEvent, QFinalState
from controller.controller import Controller
from modules.btp.prepare import Prepare

ctrl: Controller


class Btp(QState):
    def __init__(self, controller: Controller, menu: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu)
        self.reset = Reset(self)
        self.report_data = ReportData(self)
        self.menu = Menu(self)
        self.setInitialState(self.reset)
        menu.addTransition(ctrl.menu.menu['Главное меню'].button['БТП 020'].clicked, self)
        self.reset.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(ctrl.menu.prepare_menu.done.clicked, self.menu)
        self.menu.addTransition(ctrl.button['back'].clicked, self.finish)

        self.prepare = Prepare(controller=ctrl, menu_state=self.menu)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.reset_prepare()
        ctrl.menu.menu['БТП 020'].reset()


class ReportData(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu('Подготовка к испытанию')


class Menu(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu('БТП 020')
        ctrl.show_panel('меню')
        ctrl.button_enable('back up down yes')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl.menu.active = False
