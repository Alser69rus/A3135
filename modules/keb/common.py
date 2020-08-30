from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller


class ResetPtc(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.rdkp_0 = Rdkp0(self)
        self.ptc_0 = Ptc0(self)
        self.check_ptc_0 = CheckPtc0(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.rdkp_0)
        self.rdkp_0.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_neutral, self.ptc_0)
        self.ptc_0.addTransition(self.ptc_0.success, self.finish)
        self.ptc_0.addTransition(self.ptc_0.fail, self.check_ptc_0)
        self.check_ptc_0.addTransition(ctrl.server_updated, self.check_ptc_0)
        self.check_ptc_0.addTransition(self.check_ptc_0.done, self.finish)


class Rdkp0(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "- 0 -".')


class Ptc0(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Проверка давления в ТЦ2.')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            self.success.emit()
        else:
            self.fail.emit()


class CheckPtc0(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Сбросьте до 0 МПа давление в магистрали ТЦ2.')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            self.done.emit()


class SetPtc(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.rdkp_2 = Rdkp2(self)
        self.ptc_035 = Ptc035(self)
        self.check_ptc_035 = CheckPtc035(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.rdkp_2)
        self.rdkp_2.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_two, self.ptc_035)
        self.ptc_035.addTransition(self.ptc_035.success, self.finish)
        self.ptc_035.addTransition(self.ptc_035.fail, self.check_ptc_035)
        self.check_ptc_035.addTransition(ctrl.server_updated, self.check_ptc_035)
        self.check_ptc_035.addTransition(ctrl.button['yes'].clicked, self.finish)


class Rdkp2(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "КЭБ 208".')


class Ptc035(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Проверка давления в ТЦ2. Норма: не менее 0,35 МПа.')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            self.success.emit()
        else:
            self.fail.emit()


class CheckPtc035(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Установите давление не менее 0,35 МПа в магистрали ТЦ2.')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class SetPim(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.tank = Tank(self)
        self.pim = Pim(self)
        self.check_pim = CheckPim(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.tank)
        self.tank.addTransition(ctrl.switch_with_neutral['o-p-t'].state_one, self.pim)
        self.pim.addTransition(self.pim.success, self.finish)
        self.pim.addTransition(self.pim.fail, self.check_pim)
        self.check_pim.addTransition(ctrl.server_updated, self.check_pim)
        self.check_pim.addTransition(ctrl.button['yes'].clicked, self.finish)


class Tank(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Включите тумблер "НАКОП. РЕЗ." в положение "ЗАР.".')


class Pim(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Проверка давления в импульсной магистрали (норма 0,49-0,51 МПа).')
        if 0.49 <= ctrl.manometer['p im'].get_value() <= 0.51:
            self.success.emit()
        else:
            self.fail.emit()


class CheckPim(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Установите давление в импульсной магистрали в пределах 0,49-0,51 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if 0.49 <= ctrl.manometer['p im'].get_value() <= 0.51:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class SetPupr(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.upr_rd = UprRd(self)
        self.pupr = Pupr(self)
        self.check_pupr = CheckPupr(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].high_value, self.pupr)
        self.pupr.addTransition(self.pupr.success, self.finish)
        self.pupr.addTransition(self.pupr.fail, self.check_pupr)
        self.check_pupr.addTransition(ctrl.server_updated, self.check_pupr)
        self.check_pupr.addTransition(ctrl.button['yes'].clicked, self.finish)


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Включите тумблер "УПР РД 042".</p>')


class Pupr(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Проверка давления Р упр рд/сд. Норма: 0,38-0,40 МПа.</p>')
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.40:
            self.success.emit()
        else:
            self.fail.emit()


class CheckPupr(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Установите давление в управления РД/СД в пределах 0,38-0,40 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.40:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class PreparePressure(QState):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.set_pim = SetPim(self)
        self.keb = Keb(self)
        self.rd = Rd(self)
        self.set_pupr = SetPupr(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.set_pim)
        self.set_pim.addTransition(self.set_pim.finished, self.keb)
        self.keb.addTransition(ctrl.switch['keb 208'].high_value, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].high_value, self.set_pupr)
        self.set_pupr.addTransition(self.set_pupr.finished, self.finish)


class Keb(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Включите тумблер "КЭБ 208".</p>')


class Rd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Включите тумблер "РД 042".</p>')
