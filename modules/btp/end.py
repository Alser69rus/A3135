from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller

ctrl: Controller


class Ending(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.air = Air(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.air)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст манометры')
        ctrl.button_enable('back')


class Air(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключить пневмотумблер "БТП К СТЕНДУ".</p>'
                     f'<p>Включить тумблер "ВХОД" в положение "КУ"</p>')
