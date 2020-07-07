from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller
p = None


class Empty(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['РД 042']
        parent.menu.addTransition(menu.button['Время отпуска'].clicked, self)

        self.start = Start(self)
        self.pressure_check = common.PressureCheck(self)
        self.ptc = Ptc(self)
        self.set_ptc = SetPtc(self)
        self.upr_rd = UprRd(self)
        self.wait_035 = Wait035(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.ptc)
        self.ptc.addTransition(self.ptc.success, self.upr_rd)
        self.ptc.addTransition(self.ptc.fail, self.set_ptc)
        self.set_ptc.addTransition(ctrl.server_updated, self.set_ptc)
        self.set_ptc.addTransition(ctrl.button['yes'].clicked, self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].low_value, self.wait_035)
        self.wait_035.addTransition(ctrl.server_updated, self.wait_035)
        self.wait_035.addTransition(self.wait_035.done, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.rd.empty.reset()


class Ptc(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('Проверка давления в магистрали ТЦ2, норма не менее 0,35 МПа.')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            self.success.emit()
        else:
            self.fail.emit()


class SetPtc(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('<p>Установите давление в магистрали ТЦ2 не менее 0,35 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('Выключите тумблер "УПР. РД 042".')


class Wait035(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        p = ctrl.manometer['p tc2'].get_value()
        ctrl.setText(f'<p>Ожидается снижение давления до 0,35 МПа.</p>'
                     f'<p>Давление в ТЦ2: {p:.3f} МПа.</p>')
        if p <= 0.35:
            self.done.emit()
            ctrl.rd.empty.start()
            ctrl.graph.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ctrl.rd.empty.update()
        p = ctrl.manometer['p tc2'].get_value()
        if p < 0.005:
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст график')
        ctrl.show_button('back')
        if ctrl.rd.empty.result():
            ctrl.success()
        else:
            ctrl.fail()

        t = ctrl.rd.empty.text()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времени снижения давления в ТЦ (отпуск)</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время снижения давления<br>(с 0,35 до 0 МПа)</td><td>не более 10</td>'
                     f'<td align="center">{t}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
