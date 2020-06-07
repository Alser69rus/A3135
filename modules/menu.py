from PyQt5.QtCore import QState, QEvent, QFinalState
from PyQt5.QtWidgets import QPushButton
from controller.controller import Controller
from ui.main_menu import MainMenu

ctrl: Controller
menu: MainMenu


class MenuState(QState):
    def __init__(self, controller: Controller):
        super().__init__(parent=controller.stm)
        global ctrl, menu
        ctrl = controller
        menu = ctrl.menu

        self.main_menu = Menu('Главное меню', self)
        self.btp: QState = SubMenu(self.main_menu, menu.main_btp, 'БТП 020', self)
        self.rd: QState = SubMenu(self.main_menu, menu.main_rd, 'РД 042', self)
        self.ku: QState = SubMenu(self.main_menu, menu.main_ku, 'КУ 215', self)
        self.keb: QState = SubMenu(self.main_menu, menu.main_keb, 'КЭБ 208', self)
        self.finish = QFinalState(self)
        self.setInitialState(self.main_menu)
        self.main_menu.addTransition(menu.main_exit.clicked, self.finish)
        self.finished.connect(ctrl.form.close)

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('меню')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl.menu.active = False


class SubMenu(QState):
    def __init__(self, main_menu: QState, button: QPushButton, menu_name: str, parent=None):
        super().__init__(parent=parent)
        self.reset = Reset(parent=self)
        self.report_data = Menu('Подготовка к испытанию', parent=self)
        self.menu = Menu(menu_name=menu_name, parent=self)
        self.finish = QFinalState(self)
        self.setInitialState(self.reset)
        self.reset.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(menu.prepare_menu.done.clicked, self.menu)
        self.menu.addTransition(ctrl.button['back'].clicked, self.finish)
        main_menu.addTransition(button.clicked, self)
        self.addTransition(self.finished, main_menu)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.reset_prepare()
        menu.menu['БТП 020'].reset()
        menu.menu['РД 042'].reset()
        menu.menu['КУ 215'].reset()
        menu.menu['КЭБ 208'].reset()


class Menu(QState):
    def __init__(self, menu_name: str, parent=None):
        super().__init__(parent=parent)
        self.menu_name = menu_name

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu(self.menu_name)
