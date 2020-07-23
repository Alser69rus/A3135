from PyQt5.QtCore import QState, QEvent, QFinalState

from controller.controller import Controller
from modules.keb.data import KebData
from modules.keb.empty import Empty
from modules.keb.end import End
from modules.keb.fill import Fill
from modules.keb.junctions import Junctions
from modules.keb.prepare import Prepare


class Keb(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent)
        self.reset = Reset(self)
        self.disable_menu = DisableMenu(self)
        self.report_data = ReportData(self)
        self.menu = Menu(self)
        parent.addTransition(ctrl.menu.menu['Главное меню'].button['КЭБ 208'].clicked, self)

        self.setInitialState(self.reset)
        self.reset.addTransition(self.disable_menu)
        self.disable_menu.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(ctrl.menu.prepare_menu.done.clicked, self.menu)
        self.menu.addTransition(ctrl.button['back'].clicked, self.finish)

        self.prepare = Prepare(self)
        self.fill = Fill(self)
        self.junctions = Junctions(self)
        self.empty = Empty(self)
        self.end = End(self)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.menu.reset_prepare()
        ctrl.menu.menu['КЭБ 208'].reset()
        ctrl.keb = KebData()


class DisableMenu(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        menu = ctrl.menu.menu['КЭБ 208']
        buttons = [
            'Время торможения',
            'Герметичность соединений',
            'Время отпуска',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(False)


class ReportData(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_menu('Подготовка к испытанию')
        buttons = (
            'Дата изготовления: ',
            'Номер тепловоза: ',
            'Номер секции: ',
        )
        for name in buttons:
            button = ctrl.menu.prepare_menu.menu.button[name]
            button.data = ' '
            button.setVisible(False)
        ctrl.menu.prepare_menu.update_fields()

    def onExit(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        buttons = (
            'Дата изготовления: ',
            'Номер тепловоза: ',
            'Номер секции: ',
        )
        for name in buttons:
            button = ctrl.menu.prepare_menu.menu.button[name]
            button.setVisible(True)


class Menu(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_menu('КЭБ 208')
        ctrl.show_panel('меню')
        ctrl.show_button('back up down yes')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.menu.active = False
