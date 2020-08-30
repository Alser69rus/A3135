from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.keb.report import Report

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
        menu = ctrl.menu.menu['КЭБ 208']
        parent.menu.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.keb = Keb(self)
        self.rdkp = RdKp(self)
        self.ptc = Ptc(self)
        self.upr_rd = UprRd(self)
        self.pupr = Pupr(self)
        self.rd = Rd(self)
        self.tank_2 = Tank2(self)
        self.voltage = Voltage(self)
        self.uninstall = Uninstall(self)
        self.air = Air(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.pupr)
        self.pupr.addTransition(ctrl.server_updated, self.pupr)
        self.pupr.addTransition(self.pupr.done, self.keb)
        self.keb.addTransition(ctrl.switch['keb 208'].low_value, self.rdkp)
        self.rdkp.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_neutral, self.ptc)
        self.ptc.addTransition(ctrl.server_updated, self.ptc)
        self.ptc.addTransition(self.ptc.done, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].low_value, self.tank_2)
        self.tank_2.addTransition(ctrl.server_updated, self.tank_2)
        self.tank_2.addTransition(self.tank_2.done, self.voltage)
        self.voltage.addTransition(ctrl.switch['50-100'].low_value, self.uninstall)
        self.uninstall.addTransition(ctrl.button['yes'].clicked, self.air)
        self.air.addTransition(ctrl.server_updated, self.air)
        self.air.addTransition(self.air.done, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')


class Keb(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "КЭБ208".')


class RdKp(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106" в нейтральное положение.')


class Ptc(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Ожидается сброс давления до 0 МПа в магистрали ТЦ2.')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            self.done.emit()


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "УПР РД 042".')


class Pupr(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Ожидается сброс давления в магистрали управления РД/СД до 0 МПа.')
        if ctrl.manometer['p upr'].get_value() < 0.005:
            self.done.emit()


class Rd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "РД 042".')


class Tank2(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        p = ctrl.manometer["p tm"].get_value()
        ctrl.setText(f'<p>Включите тумблер "КМ" в положение "ТОРМОЖЕНИЕ".</p>'
                     f'<p>Давление в накопительном резервуаре: '
                     f'{p:.3f} МПа.</p>')
        if p < 0.4:
            self.done.emit()


class Voltage(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText('<p>Установите переключатель "50 В - 110 В" в положение "50 В".</p>')


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText('<p>Отключите кабель от КЭБ 208. Снимите РД 042 и КЭБ 208 с прижимов.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class Air(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        p = ctrl.manometer['p tm'].get_value()
        ctrl.setText(f'<p>Включите тумблер "РД 042" и сбросьте давление в тормозной магистрали до 0 МПа.</p>'
                     f'<p><font color="red">ВНИМАНИЕ! Сброс давления происходит через прижим "РД 042".</font></p>'
                     f'<p>Давление в ТМ: {p:.3f} МПа.</p>')

        if p <= 0.005:
            self.done.emit()
