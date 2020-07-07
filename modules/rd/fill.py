from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller
p = None


class Fill(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        ctrl = parent.controller
        self.controller = ctrl
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['РД 042']
        parent.menu.addTransition(menu.button['Время наполнения'].clicked, self)

        self.start = Start(self)
        self.pressure_check = common.PressureCheck(self)
        self.rdkp_rd = RdkpRd(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.rdkp_rd)
        self.rdkp_rd.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_one, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.rd.fill.reset()


class RdkpRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('<p>Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "РД 042".</p>')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()
        ctrl.rd.fill.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ctrl.rd.fill.update()
        p = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        if t > 20 or p >= 0.35:
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст')
        ctrl.show_button('back')
        if ctrl.rd.fill.result():
            ctrl.success()
        else:
            ctrl.fail()

        t = ctrl.rd.fill.text()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времмени наполнения ТЦ (торможение)</caption>'
                     f'<tr><th>Наименование</th><th>Норма, МПа</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время наполнения ТЦ2<br>(с 0 до 0,35 МПа)</td><td>не более 4 с</td>'
                     f'<td align="center">{t}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
