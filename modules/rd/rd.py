from PyQt5.QtCore import QState, QEvent, QFinalState
from controller.controller import Controller
from modules.rd.data import RdData
from modules.rd.prepare import Prepare
from modules.rd.fill import Fill
from modules.rd.sensitivity import Sensitivity
from modules.rd.empty import Empty
from modules.rd.valve import Valve
from modules.rd.junctions import Junctions

ctrl: Controller


class Rd(QState):
    def __init__(self, controller: Controller, menu: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.controller = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu)
        self.reset = Reset(self)
        self.disable_menu = DisableMenu(self)
        self.report_data = ReportData(self)
        self.menu = Menu(self)
        menu.addTransition(ctrl.menu.menu['Главное меню'].button['РД 042'].clicked, self)

        self.setInitialState(self.reset)
        self.reset.addTransition(self.disable_menu)
        self.disable_menu.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(ctrl.menu.prepare_menu.done.clicked, self.menu)
        self.menu.addTransition(ctrl.button['back'].clicked, self.finish)

        self.prepare = Prepare(self)
        self.fill = Fill(self)
        self.sensitivity = Sensitivity(self)
        self.empty = Empty(self)
        self.valve = Valve(self)
        self.junctions = Junctions(self)

        #
        # self.ending.report.addTransition(ctrl.report.exit.clicked, self.finish)
        # self.ending.report.addTransition(ctrl.button['back'].clicked, self.finish)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.reset_prepare()
        ctrl.menu.menu['РД 042'].reset()
        ctrl.rd = RdData()


class DisableMenu(QState):
    def onEntry(self, event: QEvent) -> None:
        menu = ctrl.menu.menu['РД 042']
        buttons = [
            'Время наполнения',
            'Поддержание давления',
            'Время отпуска',
            'Герметичность соединений',
            'Герметичность клапана',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(False)


class ReportData(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu('Подготовка к испытанию')


class Menu(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_menu('РД 042')
        ctrl.show_panel('меню')
        ctrl.show_button('back up down yes')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl.menu.active = False
