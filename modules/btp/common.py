from PyQt5.QtCore import QState, QEvent
from PyQt5.QtCore import pyqtSignal
from controller.controller import Controller

ctrl: Controller


class Common:
    def __init__(self, controller: Controller):
        global ctrl
        ctrl = controller
        self.Ppm = Ppm
        self.Pim = Pim
        self.ElBreaking = ElBreaking
        self.Speed60 = Speed60
        self.Enter = Enter
        self.KU215 = KU215
        self.Tank = Tank


class Ppm(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Установите давление в питательной магистрали в пределах 0,75...1,0 МПа.</p>'
        ctrl.setText(text)
        if 0.75 <= ctrl.manometer['p pm'].get_value() <= 1.0:
            self.done.emit()


class Pim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Необходимо сбросить до нуля давление в импульсной магистрали. ' \
               f'Для этого переведите ручку крана в отпускное положение.</p>'

        ctrl.setText(text)
        if ctrl.manometer['p im'].get_value() < 0.005:
            self.done.emit()


class ElBreaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."</p>'
        ctrl.setText(text)


class Speed60(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Выключите тумблер "> 60 км/ч"</p>'
        ctrl.setText(text)


class Enter(QState):
    def __init__(self, state: str, parent=None):
        super().__init__(parent=parent)
        self.state = state

    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Включите тумблер "ВХОД" в положение "{self.state}".</p>'
        ctrl.setText(text)


class KU215(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.setText(f'<p>Включите тумблер "КУ 215".</p>')


class Tank(QState):
    def __init__(self, state: str, parent=None):
        super().__init__(parent=parent)
        self.state = state

    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.setText(f'<p>Включите тумблер "НАКОП. РЕЗ." в положение "СБРОС".</p>')
