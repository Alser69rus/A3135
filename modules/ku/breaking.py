from PyQt5.QtCore import QState, QFinalState, QEvent

from controller.controller import Controller
from modules.ku.common import Common

ctrl: Controller


class Breaking(QState):
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
        parent.menu.addTransition(menu.button['Ступени торможения'].clicked, self)

        self.start = Start(self)
        self.prepare_pressure = common.prepare_pressure(self)
        self.pressure_0 = common.pressure_0(self)
        self.breaking_stage_1 = common.breaking_stage(self, 1)
        self.breaking_stage_2 = common.breaking_stage(self, 2)
        self.breaking_stage_3 = common.breaking_stage(self, 3)
        self.breaking_stage_4 = common.breaking_stage(self, 4)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.pressure_0)
        self.pressure_0.addTransition(ctrl.server_updated, self.pressure_0)
        self.pressure_0.addTransition(ctrl.button['yes'].clicked, self.breaking_stage_1)
        self.breaking_stage_1.addTransition(self.breaking_stage_1.finished, self.breaking_stage_2)
        self.breaking_stage_2.addTransition(self.breaking_stage_2.finished, self.breaking_stage_3)
        self.breaking_stage_3.addTransition(self.breaking_stage_3.finished, self.breaking_stage_4)
        self.breaking_stage_4.addTransition(self.breaking_stage_4.finished, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график прогресс')
        ctrl.graph.show_graph('p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.ku.breaking_stage.reset()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('график текст')
        ctrl.show_button('back')
        if ctrl.ku.breaking_stage.result():
            ctrl.success()
        else:
            ctrl.fail()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка давлений в импульсной магистрали на ступенях торможения</caption>'
                     f'<tr><th>Ступень</th><th>Норма, МПа</th><th>Р им факт, МПа</th></tr>'
                     f'<tr><td>1 ступень</td><td align="center">0,1-0,13</td>'
                     f'<td align="center">{ctrl.ku.breaking_stage.text(0)}</td></tr>'
                     f'<tr><td>2 ступень</td><td align="center">0,17-0,20</td>'
                     f'<td align="center">{ctrl.ku.breaking_stage.text(1)}</td></tr>'
                     f'<tr><td>3 ступень</td><td align="center">0,27-0,30</td>'
                     f'<td align="center">{ctrl.ku.breaking_stage.text(2)}</td></tr>'
                     f'<tr><td>4 ступень</td><td align="center">0,37-0,40</td>'
                     f'<td align="center">{ctrl.ku.breaking_stage.text(3)}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
