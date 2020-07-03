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
        self.ku_215_on = KU215On(self)
        self.breaking = Breaking(self)
        self.ku_215_off = KU215Off(self)
        self.enter = Enter(self)
        self.disconnect_bto = DisconnectBTO(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.air)
        self.air.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.ku_215_on)
        self.ku_215_on.addTransition(ctrl.switch['ku 215'].high_value, self.breaking)
        self.breaking.addTransition(ctrl.button['yes'].clicked, self.ku_215_off)
        self.ku_215_off.addTransition(ctrl.switch['ku 215'].low_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, self.disconnect_bto)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст манометры')
        ctrl.button_enable('back')


class Air(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключить пневмотумблер "БТП К СТЕНДУ".</p>'
                     f'<p>Включить тумблер "ВХОД" в положение "КУ"</p>')


class KU215On(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "КУ215".</p>')


class Breaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        ctrl.setText(f'<p>Выполните несколько торможений и отпусков краном 215 до '
                     f'состояния когда ТЦ перестанут наполняться.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class KU215Off(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.setText(f'<p>Выключите тумблер "КУ 215".</p>')


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переключите тумблер "ВХОД" в положение "- 0 -".</p>')


class DisconnectBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        ctrl.setText(f'<p>Отсоедините пневматические рукова и электрические шлейфы от БТО.</p>'
                     f'<p>Снимите КУ 215 с прижима.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
