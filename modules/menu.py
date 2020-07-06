from PyQt5.QtCore import QState, QEvent
from controller.controller import Controller
from modules.btp.btp import Btp
from modules.rd.rd import Rd

ctrl: Controller


class MenuState(QState):
    def __init__(self, controller: Controller):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        ctrl.menu.menu['Главное меню'].button['Выход'].clicked.connect(ctrl.form.close)
        self.btp = Btp(controller=ctrl, menu=self)
        self.rd = Rd(controller=ctrl, menu=self)

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('меню')
        ctrl.show_menu('Главное меню')
        ctrl.button_enable('back up down yes')
        ctrl.menu.active = True
