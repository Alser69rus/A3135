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
        self.rdkp_0 = RdKp0(self)
        self.tank_2 = Tank2(self)
        self.uninstall = Uninstall(self)
        self.report = Report(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.ptc)
        self.ptc.addTransition(ctrl.server_updated, self.ptc)
        self.ptc.addTransition(self.ptc.done, self.rd)
        self.rd.addTransition(ctrl.switch['rd 042'].low_value, self.rdkp_0)
        self.rdkp_0.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_neutral, self.tank_2)
        self.tank_2.addTransition(ctrl.server_updated, self.tank_2)
        self.tank_2.addTransition(self.tank_2.done, self.uninstall)
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


class RdKp0(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РД 042 - 0 - КЭБ 208" в положение "- 0 -".')


class Tank2(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        p = ctrl.manometer["p im"].get_value()
        ctrl.setText(f'<p>Включите тумблер "НАКОП. РЕЗ." в положение "СБРОС", '
                     f'и установите давление в накопительном резервуаре равным 0 МПа. </p>'
                     f'<p>Давление в накопительном резервуаре: '
                     f'{p:.3f} МПа.</p>')
        if p < 0.005:
            self.done.emit()


class Uninstall(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes')
        ctrl.setText('<p>Снимите РД 042 с прижима.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
