from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.keb.common import SetPtc, PreparePressure


class Empty(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)

        self.controller: Controller = parent.controller
        ctrl = self.controller

        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КЭБ 208']
        parent.menu.addTransition(menu.button['Время отпуска'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = PreparePressure(self)
        self.set_ptc = SetPtc(self)
        self.auto = Auto(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.set_ptc)
        self.set_ptc.addTransition(self.set_ptc.finished, self.auto)
        self.auto.addTransition(ctrl.server_updated, self.auto)
        self.auto.addTransition(self.auto.done, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.keb.empty.reset()


class Auto(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.setText('Нажмите и удерживайте кнопку "АВТ. ОТПУСК".')
        if ctrl.manometer['p tc2'].get_value() <= 0.35:
            ctrl.keb.empty.start()
            ctrl.graph.start()
            self.done.emit()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.graph.update()
        ctrl.setText('Производится измерение времени снижения давления с 0,35 до 0.04 МПа, норма: не более 4 с.')
        if ctrl.manometer['p tc2'].get_value() < 0.04:
            ctrl.keb.empty.stop()
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.keb.empty.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времени снижения давления в ТЦ (отпуск).</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время снижения давления в ТЦ2<br>(с 0,35 до 0,04 МПа)</td><td>не более 4</td>'
                     f'<td align="center">{ctrl.keb.empty.text()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
