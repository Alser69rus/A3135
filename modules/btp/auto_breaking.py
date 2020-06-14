from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller

DATA_SIZE = 100
EPS = 0.005
DELAY = 5


class AutoBreaking(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['торможение автоматическое'].clicked, self)

        self.start = Start(self)
        self.pim = Pim(self)
        self.check_1 = Check(stage=0, parent=self)
        self.check_2 = Check(stage=1, parent=self)
        self.check_3 = Check(stage=2, parent=self)
        self.check_4 = Check(stage=3, parent=self)
        self.check_5 = Check(stage=4, parent=self)
        self.check_6 = Check(stage=5, parent=self)
        self.check_7 = Check(stage=6, parent=self)
        self.check_8 = Check(stage=7, parent=self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.check_1)
        self.check_1.addTransition(self.check_1.finished, self.check_2)
        self.check_2.addTransition(self.check_2.finished, self.check_3)
        self.check_3.addTransition(self.check_3.finished, self.check_4)
        self.check_4.addTransition(self.check_4.finished, self.check_5)
        self.check_5.addTransition(self.check_5.finished, self.check_6)
        self.check_6.addTransition(self.check_6.finished, self.check_7)
        self.check_7.addTransition(self.check_7.finished, self.check_8)
        self.check_8.addTransition(self.check_8.finished, self.show_result)
        self.show_result.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.button_enable('back')
        ctrl.btp.auto_breaking.tc1 = [-1.0] * 8
        ctrl.btp.auto_breaking.tc2 = [-1.0] * 8
        ctrl.menu.current_menu.current_button.set_normal()


class Pim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переведите ручку крана в отпускное положение и сбросьте давление до 0 МПа.</p>')
        if ctrl.manometer['p im'].get_value() <= 0.005:
            self.done.emit()


class Ppm(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Установите давление в питательной магистрали в пределах 0,75...1,0 МПа.</p>')
        if 0.75 <= ctrl.manometer['p pm'].get_value() <= 1.0:
            self.done.emit()


class ElBreaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ.".</p>')


class Speed60(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключите тумблер ">60 км/ч".</p>')


class KU215(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "КУ 215".</p>')


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "ВХОД" в положение "ВР".</p>')


class HandlePosition(QState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        step = (
            'в первое положение',
            'во второе положение',
            'в третье положение',
            'в четвертое положение',
            'в третье положение',
            'в во второе положение',
            'в первое положение',
            'в отпускное положение',
        )
        self.position: str = step[stage]

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Переведите рукоятку в {self.position}.')


class CheckHandlePosition(QState):
    done = pyqtSignal()

    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        if stage == 0:
            self.check = lambda p: p > ctrl.btp.auto_breaking.range[7][1]
        elif 1 <= stage <= 3:
            self.check = lambda p: p > ctrl.btp.auto_breaking.range[stage - 1][1]
        elif 4 <= stage <= 7:
            self.check = lambda p: p < ctrl.btp.auto_breaking.range[stage - 1][0]
        else:
            self.check = None

    def onEntry(self, event: QEvent) -> None:
        pim = ctrl.manometer['p im'].get_value()
        if self.check(pim):
            ctrl.graph.reset()
            ctrl.graph.start()
            self.done.emit()


class PressureStabilization(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        data = ctrl.graph.data['p im']
        data = data[-DATA_SIZE:]
        dp = max(data) - min(data)
        dt = ctrl.graph.dt
        ctrl.setText(f'<p>Ожидается стабилизация давления в импульсной магистрали.</p>'
                     f'<p>Текущая разность давлений: {dp:.3f} МПа.</p>'
                     f'<p>Времени прошло с начала измерения: {dt:.1f} с.</p>')
        if dp <= EPS and dt >= DELAY:
            self.done.emit()


class SaveResult(QFinalState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        self.stage = stage

    def onEntry(self, event: QEvent) -> None:
        ctrl.btp.auto_breaking.tc1[self.stage] = ctrl.manometer['p tc1'].get_value()
        ctrl.btp.auto_breaking.tc2[self.stage] = ctrl.manometer['p tc2'].get_value()


class Check(QState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        self.ppm = Ppm(self)
        self.el_breaking = ElBreaking(self)
        self.speed_60 = Speed60(self)
        self.ku_215 = KU215(self)
        self.enter = Enter(self)
        self.handle_position = HandlePosition(stage=stage, parent=self)
        self.check_handle_position = CheckHandlePosition(stage=stage, parent=self)
        self.pressure_stabilization = PressureStabilization(self)
        self.save_result = SaveResult(stage=stage, parent=self)

        self.setInitialState(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_one, self.handle_position)
        self.handle_position.addTransition(self.check_handle_position)
        self.check_handle_position.addTransition(ctrl.server_updated, self.check_handle_position)
        self.check_handle_position.addTransition(self.check_handle_position.done, self.pressure_stabilization)
        self.pressure_stabilization.addTransition(ctrl.server_updated, self.pressure_stabilization)
        self.pressure_stabilization.addTransition(self.pressure_stabilization.done, self.save_result)


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.show_panel('текст')
        text = f'<p><table border="2" cellpadding="4" >' \
               f'<caption>Проверка ступеней торможения и отпуска при действии автоматического томоза</caption>' \
               f'<tr><th>Ступень</th><th>Норма, МПа</th><th>ТЦ1 факт, МПа</th><th>ТЦ2 факт, МПа</th></tr>' \
               f'<tr><th colspan="4">Торможение</th></tr>'

        for i in range(4):
            text += self.get_row(i)
        text += f'<tr><th colspan="4">Отпуск</th></tr>'
        for i in range(4, 8):
            text += self.get_row(i)

        text += f'</table></p>'
        text += f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>'
        ctrl.setText(text)

        if ctrl.btp.auto_breaking.success():
            ctrl.menu.current_menu.current_button.set_success()
        else:
            ctrl.menu.current_menu.current_button.set_fail()

    def get_row(self, row: int):
        data = ctrl.btp.auto_breaking
        stage = data.stage[row]
        rang = data.range_as_text(row)
        tc1 = data.tc1_as_text(row)
        tc2 = data.tc2_as_text(row)
        return f'<tr><td>   {stage}  </td><td>   {rang}   </td>' \
               f'<td align="center">   {tc1}   </td><td align="center">   {tc2}   </td></tr>'
