from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller


class AutoBreaking(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['торможение автоматическое'].clicked, self)

        self.start = Start(self)

        self.setInitialState(self.start)


class Start(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')
        text = f'<p><font color="red">ВНИМАНИЕ! БТО испытывается с исправным КУ 215.</font></p>' \
               f'<p>Установите КУ 215 на прижим, включите пневмотумблер "ПРИЖИМ КУ 215".</p>' \
               f'<p>Включите тумблер "КУ 215".</p>'

        ctrl.setText(text)
        if ctrl.switch['ku 215'].get_value():
            self.done.emit()
