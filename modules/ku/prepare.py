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
        self.ku = KU(self)
        self.tc820 = Tc820(self)
        self.leak = Leak(self)
        self.enable_menu = EnableMenu(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.install)
        self.install.addTransition(ctrl.button['yes'].clicked, self.ku)
        self.ku.addTransition(ctrl.switch['ku 215'].high_value, self.tc820)
        self.tc820.addTransition(ctrl.switch['tc 820'].low_value, self.leak)
        self.leak.addTransition(ctrl.switch['leak 0,5'].low_value, self.enable_menu)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back yes')
        ctrl.normal()


class Install(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Установите КУ 215 на прижим.</p>'
                     f'<p>Откройте кран на атмосферной трубе, отходящей от плиты прижима КУ 215.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class KU(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "КУ 215".')


class Tc820(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "ТЦ2 8 л - 20 л" в положение "8 л".')


class Leak(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Отключите тумблер "УТЕЧКА ø0,5".')


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
