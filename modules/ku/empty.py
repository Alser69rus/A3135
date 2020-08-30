from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


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
        menu = ctrl.menu.menu['КУ 215']
        parent.menu.addTransition(menu.button['Снижение давления'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_4 = common.pressure_4(self)
        self.handle_0 = Handle0(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_4)
        self.pressure_4.addTransition(ctrl.server_updated, self.pressure_4)
        self.pressure_4.addTransition(ctrl.button['yes'].clicked, self.handle_0)
        self.handle_0.addTransition(ctrl.server_updated, self.handle_0)
        self.handle_0.addTransition(self.handle_0.done, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.empty.reset()


class Handle0(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Переведите ручку КУ 215 в отпускное положение за один прием.</p>'
                     f'<p>Будет зарегестрировано время снижения давления ТЦ2 с 0,35 до 0 МПа. '
                     f'Норма: не более 10 с. </p>')
        if ctrl.manometer['p tc2'].get_value() <= 0.35:
            ctrl.graph.start()
            ctrl.ku.empty.start()
            self.done.emit()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ctrl.setText('Измеряется время снижения давления ТЦ2 до 0 МПа. Норма: не более 10 с.')
        if ctrl.manometer['p tc2'].get_value() <= 0.01:
            ctrl.ku.empty.stop()
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.ku.empty.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времени снижения давления ТЦ2</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>Время факт, с</th></tr>'
                     f'<tr><td>Время снижения Р тц2<br>(с 0,35 до 0 МПа)</td><td>не более 10</td>'
                     f'<td align="center">{ctrl.ku.empty.text()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
