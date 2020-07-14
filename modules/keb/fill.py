from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller
from modules.keb.common import ResetPtc, PreparePressure


class Fill(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)

        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КЭБ 208']
        parent.menu.addTransition(menu.button['Время торможения'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = PreparePressure(self)
        self.reset_ptc = ResetPtc(self)
        self.rdkp = Rdkp(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)
        self.finish = QFinalState(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.reset_ptc)
        self.reset_ptc.addTransition(self.reset_ptc.finished, self.rdkp)
        self.rdkp.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_two, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.keb.fill.reset()


class Rdkp(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('<p>Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "КЭБ208".</p>')

    def onExit(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.graph.start()
        ctrl.keb.fill.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.graph.update()
        ctrl.setText('<p>Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "КЭБ208".</p>')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            ctrl.keb.fill.stop()
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.keb.fill.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времмени наполнения ТЦ (торможение)</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время наполнения ТЦ2<br>(с 0 до 0,35 МПа)</td><td>не более 4</td>'
                     f'<td align="center">{ctrl.keb.fill.text()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
