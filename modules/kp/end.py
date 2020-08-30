from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.kp.report import Report

ctrl: Controller


class End(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КП 106']
        parent.menu.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.upr_rd = UprRd(self)
        self.rd = Rd(self)
        self.kp106 = Kp106(self)
        self.km = Km(self)
        self.rdkp = RdKp(self)
        self.tc820 = Tc820(self)
        self.uninstall = Uninstall(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].low_value, self.kp106)
        self.kp106.addTransition(ctrl.switch['kp 106'].low_value, self.km)
        self.km.addTransition(ctrl.switch_with_neutral['km'].state_neutral, self.rdkp)
        self.rdkp.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_neutral, self.tc820)
        self.tc820.addTransition(ctrl.switch['tc 820'].low_value, self.uninstall)
        self.uninstall.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Отключите тумблер "УПР. РД 042".')


class Rd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Отключите тумблер "РД 042".')


class Kp106(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Отключите тумблер "КП 106".')


class Km(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "КМ" в нейтральное положение.')


class RdKp(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106" в нейтральное положение.')


class Tc820(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Установите тумблер "ТЦ2 8 л - 20 л" в положение "8 л".')


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText(f'<p>Отключите пневмотумблер "ПРИЖИМ КП 106" и снимите КП 106 со стенда.</p>'
                     f'<p>Затем отключите пневмотумблер "РД 042" и снимите РД 042 со стенда.</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')
