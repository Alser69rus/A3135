from PyQt5.QtCore import QState, QEvent
from PyQt5.QtCore import pyqtSignal

from controller.controller import Controller

ctrl: Controller

DATA_SIZE = 100
EPS = 0.005
DELAY = 5


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
        self.HandlePosition = HandlePosition
        self.CheckHandlePosition = CheckHandlePosition
        self.PressureStabilization = PressureStabilization
        self.CheckKuPressure = CheckKuPressure
        self.HandlePositionFour = HandlePositionFour


class Ppm(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Установите давление в питательной магистрали в пределах 0,75...1,0 МПа.</p>')
        if 0.75 <= ctrl.manometer['p pm'].get_value() <= 1.0:
            self.done.emit()


class Pim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Переведите ручку крана в отпускное положение и сбросьте давление в '
                     f'импульсной магистрали, ТЦ1 и ТЦ2 до нуля.</p>')
        p = [
            ctrl.manometer['p im'].get_value() <= 0.005,
            ctrl.manometer['p tc1'].get_value() <= 0.005,
            ctrl.manometer['p tc2'].get_value() <= 0.005,
        ]
        if all(p):
            self.done.emit()


class ElBreaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."</p>')


class Speed60(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Выключите тумблер ">60 км/ч".</p>')


class Enter(QState):
    def __init__(self, state: str, parent=None):
        super().__init__(parent=parent)
        self.state = state

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Включите тумблер "ВХОД" в положение "{self.state}".</p>')


class KU215(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Включите тумблер "КУ 215".</p>')


class Tank(QState):
    def __init__(self, state: str, parent=None):
        super().__init__(parent=parent)
        self.state = state

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Включите тумблер "НАКОП. РЕЗ." в положение "СБРОС".</p>')


class HandlePosition(QState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        step = (
            'в первое положение',
            'во второе положение',
            'в третье положение',
            'в четвертое положение',
            'в третье положение',
            'в во второе положение',
            'в первое положение',
            'в отпускное положение',
        )
        self.position: str = step[stage]

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Переведите рукоятку в {self.position}.')


class CheckHandlePosition(QState):
    done = pyqtSignal()

    def __init__(self, stage: int, data, parent=None):
        super().__init__(parent=parent)
        if stage == 0:
            self.check = lambda p: p > data.range[7][1]
        elif 1 <= stage <= 3:
            self.check = lambda p: p > data.range[stage - 1][1]
        elif 4 <= stage <= 7:
            self.check = lambda p: p < data.range[stage - 1][0]
        else:
            self.check = None

    def onEntry(self, event: QEvent) -> None:
        pim = ctrl.manometer['p im'].get_value()
        if self.check(pim):
            ctrl.graph.reset()
            ctrl.graph.start()
            self.done.emit()


class PressureStabilization(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        data = ctrl.graph.data['p im']
        data = data[-DATA_SIZE:]
        dp = max(data) - min(data)
        p = self.p_percent(dp)
        dt = ctrl.graph.dt
        t = self.t_percent(dt)
        value = min(t, p)
        num = round(value / 4)
        text = f'■' * num
        color = self.color(value)
        ctrl.form.progress_bar.setValue(value)
        ctrl.setText(f'<p>Ожидается стабилизация давления в импульсной магистрали.</p>')
        if dp <= EPS and dt >= DELAY:
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
        return self.norm(100 * value / DELAY)

    def p_percent(self, value: float) -> int:
        return self.norm(100 - 5 * (value - EPS) / EPS)

    @staticmethod
    def color(value: int) -> str:
        r = 200 - value * 2
        g = 0 + value * 2
        b = 50
        return f'#{r:0>2x}{g:0>2x}{b:0>2x}'


class CheckKuPressure(QState):
    done = pyqtSignal()

    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        self.stage = stage

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')

        low, high = ctrl.btp.ku_215.range[self.stage]
        p = ctrl.manometer['p im'].get_value()
        if low <= p <= high:
            self.done.emit()
        else:
            ctrl.menu.current_menu.current_button.set_fail()
            ctrl.show_panel('текст манометры')
            ctrl.setText(f'<p>Давление в импульсной магистрали  должно находится в пределах '
                         f'от {low:.3f} до {high:.3f} МПа.</p>'
                         f'<p>Текущее значение давления Рим: {p:.3f} МПа</p>'
                         f'<p>Это может говорить о неисправности КУ.</p>'
                         f'<p><br>Для возврата в меню нажмите "ВОЗВРАТ"</p>')


class HandlePositionFour(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Переведите ручку КУ 215 в четвертое положение за один прием.')
        if ctrl.manometer['p im'].get_value() >= 0.37:
            self.done.emit()
