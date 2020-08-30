from typing import List

from PyQt5.QtCore import QState, QFinalState, QEvent, QObject, pyqtSignal

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

    def pressure_4(self, parent):
        return Pressure4(parent=parent)

    def breaking_stage(self, parent, stage: int):
        return BreakingStage(parent=parent, stage=stage)


class PreparePressure(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.enter = Enter(self)
        self.ku_215 = Ku215(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['km'].state_neutral, self.ku_215)
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
        ctrl.setText(f'<p>Переведите ручку КУ 215 в отпускное положение, чтобы сбросить давление в ТЦ2 '
                     f' до 0 МПа.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class Pressure4(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переведите ручку КУ 215 в четвертое положение и установите давление в ТЦ2 '
                     f'в  пределах 0,37-0,40 МПа.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() >= 0.37:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class HandleStage(QState):
    done = pyqtSignal()

    def __init__(self, parent, stage: int):
        super().__init__(parent=parent)
        self.stage = stage

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        if self.stage == 1:
            handle = 'в первое положение'
            norm = (0.1, 0.13, 0.005)
        elif self.stage == 2:
            handle = 'во второе положение'
            norm = (0.17, 0.20, 0.14)
        elif self.stage == 3:
            handle = 'в третье положение'
            norm = (0.27, 0.30, 0.21)
        else:
            handle = 'в четвертое положение'
            norm = (0.37, 0.40, 0.31)
        ctrl.setText(f'<p>Переведите ручку КУ 215 в {handle}.</p>'
                     f'<p>После стабилизации давления в ТЦ2 будет измерено его значение. '
                     f'Норма: {norm[0]} - {norm[1]} МПа.</p>')
        if ctrl.manometer['p tc2'].get_value() >= norm[2]:
            ctrl.graph.reset()
            ctrl.graph.start()
            self.done.emit()


class Stabilize(QState):
    done = pyqtSignal()
    DATA_SIZE = 100
    EPS = 0.005
    DELAY = 5

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.p: List[float] = []

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        data = ctrl.graph.data['p tc2']
        data = data[-self.DATA_SIZE:]
        dp = max(data) - min(data)
        p = self.p_percent(dp)
        dt = ctrl.graph.dt
        t = self.t_percent(dt)
        value = min(t, p)
        ctrl.form.progress_bar.setValue(value)
        ctrl.setText(f'<p>Ожидается стабилизация давления в ТЦ2.</p>')
        if dp <= self.EPS and dt >= self.DELAY:
            ctrl.ku.breaking_stage.p.append(ctrl.manometer['p tc2'].get_value())
            self.done.emit()

    @staticmethod
    def norm(value: float) -> int:
        value = round(value)
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        return value

    def t_percent(self, value: float) -> int:
        return self.norm(100 * value / self.DELAY)

    def p_percent(self, value: float) -> int:
        return self.norm(100 - 5 * (value - self.EPS) / self.EPS)


class BreakingStage(QState):
    def __init__(self, parent, stage: int):
        super().__init__(parent=parent)

        self.handle_stage = HandleStage(self, stage)
        self.stabilize = Stabilize(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.handle_stage)
        self.handle_stage.addTransition(ctrl.server_updated, self.handle_stage)
        self.handle_stage.addTransition(self.handle_stage.done, self.stabilize)
        self.stabilize.addTransition(ctrl.server_updated, self.stabilize)
        self.stabilize.addTransition(self.stabilize.done, self.finish)
