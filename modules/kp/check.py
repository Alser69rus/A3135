from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller

ctrl: Controller


class Check(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КП 106']
        parent.menu.addTransition(menu.button['Испытание'].clicked, self)

        self.start = Start(self)
        self.gap_on = GapOn(self)
        self.measure = Measure(self)
        self.gap_off = GapOff(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.gap_on)
        self.gap_on.addTransition(ctrl.switch['gap'].high_value, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.gap_off)
        self.gap_off.addTransition(ctrl.switch['gap'].low_value, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.graph.show_graph('p tm p tc2')
        ctrl.normal()
        ctrl.kp.reset()


class GapOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РАЗРЫВ".')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ptc2 = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        ctrl.setText(f'<p>Производится проверка КП 106.<br>До завершения испытания осталось {60 - t:.1f} c.</p>')
        if ptc2 < 0.005:
            ctrl.kp.t1 = t
            ctrl.kp.t2 = ctrl.kp.t1
            ctrl.kp.p = ctrl.manometer['p tm'].get_value()
        if ptc2 >= 0.35 or t >= 60:
            ctrl.kp.t2 = t
            self.done.emit()


class GapOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "РАЗРЫВ".')


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст')
        ctrl.show_button('back')
        if ctrl.kp.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка клапана пневматического КП 106</caption>'
                     f'<tr><th>Наименование</th><th>Норма</th><th>Факт</th></tr>'
                     f'<tr><td>Давление срабатывания КП 106, МПа</td><td>0,20-0,25</td>'
                     f'<td align="center">{ctrl.kp.text_p()}</td></tr>'
                     f'<tr><td>Время наполнения ТЦ2 с 0 до 0,35 МПа, с</td><td>не более 4</td>'
                     f'<td align="center">{ctrl.kp.text_t()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
