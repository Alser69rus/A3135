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
        self.ptc = Ptc(self)
        self.upr_rd = UprRd(self)
        self.pupr = Pupr(self)
        self.rd = Rd(self)
        self.uninstall = Uninstall(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.keb)
        self.keb.addTransition(ctrl.switch['keb 208'].low_value, self.ptc)
        self.ptc.addTransition(ctrl.server_updated, self.ptc)
        self.ptc.addTransition(self.ptc.done, self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.pupr)
        self.pupr.addTransition(ctrl.server_updated, self.pupr)
        self.pupr.addTransition(self.pupr.done, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].low_value, self.uninstall)
        self.uninstall.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')


class Keb(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "КЭБ208".')


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


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText('<p>Снимите РД 042 и КЭБ 208 с прижимов.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
