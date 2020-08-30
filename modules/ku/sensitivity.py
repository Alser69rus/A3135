from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


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
        menu = ctrl.menu.menu['КУ 215']
        parent.menu.addTransition(menu.button['Утечка'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_4 = common.pressure_4(self)
        self.leak_on = LeakOn(self)
        self.measure = Measure(self)
        self.leak_off = LeakOff(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_4)
        self.pressure_4.addTransition(ctrl.server_updated, self.pressure_4)
        self.pressure_4.addTransition(ctrl.button['yes'].clicked, self.leak_on)
        self.leak_on.addTransition(ctrl.switch['leak 0,5'].high_value, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.leak_off)
        self.leak_off.addTransition(ctrl.switch['leak 0,5'].low_value, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p tm')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.sensitivity.reset()


class LeakOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УТЕЧКА ø 0,5".')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        ctrl.ku.sensitivity.update(ctrl.manometer['p tm'].get_value())
        ctrl.setText(f'<p>В течении одной минуты будет измеряться давление в импульсной магистрали '
                     f'для определения величины утечки.</p>'
                     f'<p>Осталось времени до завершения: {60 - ctrl.graph.dt:.1f} c.</p>')
        if ctrl.graph.dt >= 60:
            self.done.emit()


class LeakOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "УТЕЧКА ø 0,5".')


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.ku.sensitivity.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка величины давления в импульсной магистрали при создании утечки из нее</caption>'
                     f'<tr><th>Наименование</th><th>Норма, МПа</th><th>Р им факт, МПа</th></tr>'
                     f'<tr><td>Разница давлений</td><td align="center">не более 0,015</td>'
                     f'<td align="center">{ctrl.ku.sensitivity.text()}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
