from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


class Prepare(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КУ 215']
        parent.menu.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.install = Install(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.leak = Leak(self)
        self.tank = Tank(self)
        self.enable_menu = EnableMenu(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.install)
        self.install.addTransition(ctrl.button['yes'].clicked, self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.leak)
        self.leak.addTransition(ctrl.switch['leak 0,5'].low_value, self.tank)
        self.tank.addTransition(ctrl.switch_with_neutral['tank'].state_two, self.enable_menu)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back yes')
        ctrl.normal()


class Install(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Установите КУ 215 на прижимю</p>'
                     f'<p>Откройте кран на атмосферной трубе, отходящей от плиты прижима КУ 215.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class Leak(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Отключите тумблер "УТЕЧКА ø0,5".')


class Tank(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "НАКОП. РЕЗ." в положение "СБРОС"')


class EnableMenu(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        menu = ctrl.menu.menu['КУ 215']
        buttons = [
            'Время наполнения',
            'Снижение давления',
            'Ступени торможения',
            'Утечка',
            'Герметичность соединений',
            'Герметичность клапана',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(True)
