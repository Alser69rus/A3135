from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.btp.report import Report

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
        self.ku_215_off = KU215Off(self)
        self.disconnect_bto = DisconnectBTO(self)
        self.report = Report(parent=self, controller=controller)

        self.setInitialState(self.start)
        self.start.addTransition(self.air)
        self.air.addTransition(ctrl.button['yes'].clicked, self.ku_215_off)
        self.ku_215_off.addTransition(ctrl.switch['ku 215'].low_value, self.disconnect_bto)
        self.disconnect_bto.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст манометры')
        ctrl.show_button('back')


class Air(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText(f'<p>Выключите пневмотумблер "БТП К СТЕНДУ" '
                     f'и дождитесь разрядки питательного резервуара.</p>'
                     f'<p>Для продолжение нажмите кнопку "ДА".</p>')


class KU215Off(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Выключите тумблер "КУ 215".</p>')


class DisconnectBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText(f'<p>Отсоедините пневматические рукова и электрические шлейфы от БТО.</p>'
                     f'<p>Снимите КУ 215 с прижима.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
