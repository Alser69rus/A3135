from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


class Fill(QState):
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
        parent.menu.addTransition(menu.button['Время наполнения'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_0 = common.pressure_0(self)
        self.handle_4 = Handle4(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_0)
        self.pressure_0.addTransition(ctrl.server_updated, self.pressure_0)
        self.pressure_0.addTransition(ctrl.button['yes'].clicked, self.handle_4)
        self.handle_4.addTransition(ctrl.server_updated, self.handle_4)
        self.handle_4.addTransition(self.handle_4.done, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.fill.reset()


class Handle4(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переведите ручку КУ 215 в четвертое положение за один прием.</p>'
                     f'<p>Будет зарегестрировано время увеличения давления Рим с 0 до 0,35 МПа. '
                     f'Норма: не более 3 с. </p>')
        if ctrl.manometer['p im'].get_value() >= 0.005:
            ctrl.graph.start()
            ctrl.ku.fill.start()
            self.done.emit()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ctrl.setText('Измеряется время увеличения давления Р им с 0 до 0,35 МПа. Норма: не более 3 с.')
        if ctrl.manometer['p im'].get_value() >= 0.35:
            ctrl.ku.fill.stop()
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.ku.fill.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времени наполнения импульсной магистрали</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>Время факт, с</th></tr>'
                     f'<tr><td>Время наполнения Р им<br>(с 0 до 0,35 МПа)</td><td>не более 3</td>'
                     f'<td align="center">{ctrl.ku.fill.text()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
