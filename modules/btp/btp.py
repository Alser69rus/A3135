from PyQt5.QtCore import QState, QEvent, QFinalState
from controller.controller import Controller
from modules.btp.data import BtpData
from modules.btp.prepare import Prepare
from modules.btp.auto_breaking import AutoBreaking
from modules.btp.kvt_breaking import KvtBreaking
from modules.btp.filling import Filling
from modules.btp.tightness import Tightness
from modules.btp.emptying import Emptying
from modules.btp.substitution import Substitution
from modules.btp.speed import Speed
from modules.btp.end import Ending

ctrl: Controller


class Btp(QState):
    def __init__(self, controller: Controller, menu: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu)
        self.reset = Reset(self)
        self.disable_menu = DisableMenu(self)
        self.report_data = ReportData(self)
        self.menu = Menu(self)
        menu.addTransition(ctrl.menu.menu['Главное меню'].button['БТП 020'].clicked, self)

        self.setInitialState(self.reset)
        self.reset.addTransition(self.disable_menu)
        self.disable_menu.addTransition(self.report_data)
        self.report_data.addTransition(ctrl.button['back'].clicked, self.finish)
        self.report_data.addTransition(ctrl.menu.prepare_menu.done.clicked, self.menu)
        self.menu.addTransition(ctrl.button['back'].clicked, self.finish)

        self.prepare = Prepare(controller=ctrl, menu_state=self.menu)
        self.auto_breaking = AutoBreaking(controller=ctrl, menu_state=self.menu)
        self.kvt_breaking = KvtBreaking(controller=ctrl, menu_state=self.menu)
        self.filling = Filling(controller=ctrl, menu_state=self.menu)
        self.tightness = Tightness(controller=ctrl, menu_state=self.menu)
        self.emptying = Emptying(controller=ctrl, menu_state=self.menu)
        self.substitution = Substitution(controller=ctrl, menu_state=self.menu)
        self.speed = Speed(controller=ctrl, menu_state=self.menu)
        self.ending = Ending(controller=ctrl, menu_state=self.menu)


class Reset(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.menu.reset_prepare()
        ctrl.menu.menu['БТП 020'].reset()
        ctrl.btp = BtpData()


class DisableMenu(QState):
    def onEntry(self, event: QEvent) -> None:
        menu = ctrl.menu.menu['БТП 020']
        buttons = [
            'торможение автоматическое',
            'торможение КВТ',
            'Время наполненя ТЦ',
            'Герметичность',
            'Время снижения',
            'Замещение торможения',
            'Повышенная скорость',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(True)


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
