from PyQt5.QtCore import QState, QEvent

from controller.controller import Controller
from modules.btp.btp import Btp
from modules.keb.keb import Keb
from modules.kp.kp import Kp
from modules.ku.ku import Ku
from modules.rd.rd import Rd

ctrl: Controller


class MenuState(QState):
    def __init__(self, controller: Controller):
        super().__init__(parent=controller.stm)
        global ctrl
        self.controller: Controller = controller
        ctrl = self.controller
        ctrl.menu.menu['Главное меню'].button['Выход'].clicked.connect(ctrl.form.close)
        self.btp = Btp(controller=ctrl, menu=self)
        self.rd = Rd(self)
        self.keb = Keb(self)
        self.ku = Ku(self)
        self.kp = Kp(self)

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('меню')
        ctrl.show_menu('Главное меню')
        ctrl.show_button('back up down yes')
        ctrl.menu.active = True
