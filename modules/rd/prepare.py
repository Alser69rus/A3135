from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller


class Prepare(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        ctrl = parent.controller
        self.controller = ctrl
        common: Common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        menu = ctrl.menu.menu['РД 042']
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        parent.menu.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.tc820 = Tc820(self)
        self.set_rd = SetRd(self)
        self.rdkp_0 = Rdkp0(self)
        self.pressure_check = common.PressureCheck(self)
        self.enable_menu = EnableMenu(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.set_rd)
        self.set_rd.addTransition(ctrl.button['yes'].clicked, self.tc820)
        self.tc820.addTransition(ctrl.switch['tc 820'].high_value, self.rdkp_0)
        self.rdkp_0.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_neutral, self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.enable_menu)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back yes')
        ctrl.normal()


class Tc820(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "ТЦ2 8 л - 20 л" в положение "20 л".')


class SetRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('<p>Установите РД 042 на прижим, включите пневмотумблер "ПРИЖИМ РД 042".</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class Rdkp0(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "- 0 -".')


class EnableMenu(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        menu = ctrl.menu.menu['РД 042']
        buttons = [
            'Время наполнения',
            'Поддержание давления',
            'Время отпуска',
            'Герметичность соединений',
            'Герметичность клапана',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(True)
