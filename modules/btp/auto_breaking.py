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
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back yes')
        text = f'<p>Переведите ручку КУ 215 в 1 положение</p>' \
               f'<p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)


class Check1(QState):
    def onEntry(self, event: QEvent) -> None:
        pass
