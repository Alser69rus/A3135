from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller
p = None


class Sensitivity(QState):
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
        parent.menu.addTransition(menu.button['Поддержание давления'].clicked, self)

        self.start = Start(self)
        self.pressure_check = common.PressureCheck(self)
        self.leak_on = LeakOn(self)
        self.measure = Measure(self)
        self.leak_off = LeakOff(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.leak_on)
        self.leak_on.addTransition(ctrl.switch['leak 1'].high_value, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.leak_off)
        self.leak_off.addTransition(ctrl.switch['leak 1'].low_value, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.rd.sensitivity.reset()


class LeakOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УТЕЧКА ТЦ ø1"')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()
        ctrl.rd.sensitivity.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        p = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        if t > 0:
            ctrl.rd.sensitivity.update(p)
        if t > 15:
            self.done.emit()


class LeakOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "УТЕЧКА ТЦ ø1"')


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст график')
        ctrl.show_button('back')
        if ctrl.rd.sensitivity.result():
            ctrl.success()
        else:
            ctrl.fail()

        dp = ctrl.rd.sensitivity.text()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка автоматического поддержания установившегося зарядного\n'
                     f'давления (чувствительность в ТЦ при создании утечки из него</caption>'
                     f'<tr><th>Наименование</th><th>Норма, МПа</th><th>ТЦ2 факт, МПа</th></tr>'
                     f'<tr><td>Чувствительность ТЦ2 за 15 с</td><td>не более 0.015</td>'
                     f'<td align="center">{dp}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
