from PyQt5.QtCore import QStateMachine, QState, QEvent


class MenuState(QState):
    def __init__(self, con):
        global ctrl
        super().__init__(parent=con.stm)
        ctrl = con

    def onEntry(self, event: QEvent) -> None:
        ctrl.form.show_panel('меню')
        ctrl.menu.active = True

    def onExit(self, event: QEvent) -> None:
        ctrl.menu.active = False
