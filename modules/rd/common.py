from PyQt5.QtCore import QState, QEvent, QFinalState
from PyQt5.QtCore import pyqtSignal

from controller.controller import Controller

ctrl: Controller

DATA_SIZE = 100
EPS = 0.005
DELAY = 5


class Common:
    def __init__(self, parent):
        global ctrl
        ctrl = parent.controller
        self.PressureCheck = PressureCheck


class Tank(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.setText('Включить тумблер "КМ" в положение "ОТПУСК".')


class CheckPim(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        if 0.52 <= ctrl.manometer['p tm'].get_value() <= 0.55:
            self.success.emit()
        else:
            self.fail.emit()


class SetPim(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        if 0.52 <= ctrl.manometer['p tm'].get_value() <= 0.55:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')
        ctrl.setText('<p>Установите давление в ТМ в пределах 0,52-0,55 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class Pim(QState):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tank = Tank(self)
        self.check_pim = CheckPim(self)
        self.set_pim = SetPim(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.tank)
        self.tank.addTransition(ctrl.switch_with_neutral['km'].state_one, self.check_pim)
        self.check_pim.addTransition(self.check_pim.success, self.finish)
        self.check_pim.addTransition(self.check_pim.fail, self.set_pim)
        self.set_pim.addTransition(ctrl.server_updated, self.set_pim)
        self.set_pim.addTransition(ctrl.button['yes'].clicked, self.finish)


class Rd042(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "РД 042".')


class UprRd042(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УПР РД 042".')


class CheckPrsd(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.42:
            self.success.emit()
        else:
            self.fail.emit()


class SetPrdsd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.setText('<p>Установите давление РД/СД в пределах 0,38-0,42 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.42:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class Prdsd(QState):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.upr_rd042 = UprRd042(self)
        self.check_prdsd = CheckPrsd(self)
        self.set_prdsd = SetPrdsd(self)
        self.finsh = QFinalState(self)

        self.setInitialState(self.upr_rd042)
        self.upr_rd042.addTransition(ctrl.switch['upr rd 042'].high_value, self.check_prdsd)
        self.check_prdsd.addTransition(self.check_prdsd.success, self.finsh)
        self.check_prdsd.addTransition(self.check_prdsd.fail, self.set_prdsd)
        self.set_prdsd.addTransition(ctrl.server_updated, self.set_prdsd)
        self.set_prdsd.addTransition(ctrl.button['yes'].clicked, self.finsh)


class PressureCheck(QState):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pim = Pim(self)
        self.rd042 = Rd042(self)
        self.prdsd = Prdsd(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.pim)
        self.pim.addTransition(self.pim.finished, self.rd042)
        self.rd042.addTransition(ctrl.switch['rd 042'].high_value, self.prdsd)
        self.prdsd.addTransition(self.prdsd.finished, self.finish)
