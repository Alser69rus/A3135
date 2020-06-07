from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal
from controller.controller import Controller

ctrl: Controller


class Prepare(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        menu = ctrl.menu.menu['БТП 020']
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu_state.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.setInitialState(self.start)
        self.start.addTransition(ctrl.server_updated, self.start)
        self.check_pim = CheckPim(self)
        self.start.addTransition(self.start.done, self.check_pim)


class Start(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')
        text = f'<p><font color="red">ВНИМАНИЕ! БТО испытывается с исправным КУ 215.</font></p>' \
               f'<p>Установить КУ 215 на прижим, включить пневмотумблер "ПРИЖИМ КУ 215".</p>' \
               f'<p>Включить тумблер "КУ 215".</p>'
        ctrl.setText(text)
        if ctrl.switch['ku 215'].get_value():
            self.done.emit()


class CheckPim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Необходимо сбросить до нуля давление в импульсной магистрали.' \
               f' Для этого переведите ручку крана в отпускное положение.</p>'
        ctrl.setText(text)
        if ctrl.manometer['p im'].get_value() < 0.005:
            self.done.emit()
