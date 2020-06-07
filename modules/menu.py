from PyQt5.QtCore import QStateMachine, QState, QEvent, QFinalState
from PyQt5.QtWidgets import QPushButton
from controller.controller import Controller
from typing import Dict
from ui.main_menu import MainMenu

ctrl: Controller
menu: MainMenu


class MenuState(QState):
    def __init__(self, controller: Controller):
        super().__init__(parent=controller.stm)
        global ctrl, menu
        ctrl = controller
        menu = ctrl.menu
        # self.main_menu = MainMenu(self)
        self.prepare_btp = ReportData(self)
        self.reset_btp = Reset(self)
        # self.btp020 = BTP020(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.main_menu)

        self.main_menu.addTransition(menu.main_exit.clicked, self.finish)
        self.main_menu.addTransition(menu.main_btp.clicked, self.prepare_btp)
        self.prepare_btp.addTransition(ctrl.button['back'].clicked, self.main_menu)
        self.prepare_btp.addTransition(menu.prepare_menu.done.clicked, self.reset_btp)
        self.reset_btp.addTransition(self.btp020)
        self.btp020.addTransition(ctrl.button['back'].clicked, self.main_menu)

        self.finished.connect(ctrl.form.close)

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('меню')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl.menu.active = False


class SubMenu(QState):
    def __init__(self, menu_name, parent=None):
        super().__init__(parent=parent)
        self.reset = Reset(parent=self)
        self.report_data = ReportData(parent=self)
        self.menu = Menu(menu_name=menu_name, parent=self)
        self.finish = QFinalState()
        self.setInitialState(self.reset)
        self.reset.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(menu.prepare_menu.done.clicked, self.menu)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.reset_prepare()
        menu.menu['БТП 020'].reset()
        menu.menu['РД 042'].reset()
        menu.menu['КУ 215'].reset()
        menu.menu['КЭБ 208'].reset()


class ReportData(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu('Подготовка к испытанию')


class Menu(QState):
    def __init__(self, menu_name: str, parent=None):
        super().__init__(parent=parent)
        self.menu_name = menu_name

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu(self.menu_name)
