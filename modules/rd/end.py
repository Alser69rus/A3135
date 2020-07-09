from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller

from modules.rd.report import Report

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
        menu = ctrl.menu.menu['РД 042']
        parent.menu.addTransition(menu.button['Завершение'].clicked, self)

        self.start = Start(self)
        self.upr_rd = UprRd(self)
        self.ptc = Ptc(self)
        self.rd = Rd(self)
        self.uninstall = Uninstall(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.ptc)
        self.ptc.addTransition(ctrl.server_updated, self.ptc)
        self.ptc.addTransition(self.ptc.done, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].low_value, self.uninstall)
        self.uninstall.addTransition(ctrl.button['yes'].clicked, self.report)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "УПР РД 042".')


class Ptc(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Ожидается сброс давления в ТЦ2 до 0 МПа.')
        if ctrl.manometer['p tc2'].get_value() < 0.005:
            self.done.emit()


class Rd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "РД 042".')


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText('<p>Снимите РД 042 с прижима.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
