from PyQt5.QtCore import QState, QFinalState, QEvent, QObject

from controller.controller import Controller

ctrl: Controller


class Common(QObject):
    def __init__(self, parent):
        super().__init__(parent=parent)
        global ctrl
        self.ctrl: Controller = parent.controller
        ctrl = self.ctrl

    def prepare_pressure(self, parent):
        return PreparePressure(parent=parent)

    def pressure_0(self, parent):
        return Pressure0(parent=parent)


class PreparePressure(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.enter = Enter(self)
        self.ku_215 = Ku215(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.finish)


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "ВХОД" в положение "- 0 -".')


class Ku215(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "КУ 215".')


class Pressure0(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переведите ручку КУ 215 в отпускное положение, чтобы сбросить давление в импульсной '
                     f'магистрали до 0 МПа.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')
