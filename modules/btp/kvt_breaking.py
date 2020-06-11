from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller


class KvtBreaking(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['торможение КВТ'].clicked, self)

        self.start = Start(self)
        self.el_breaking = ElBreaking(self)
        self.speed_60 = Speed60(self)
        self.p_im = Pim(self)
        self.enter = Enter(self)
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
        self.start.addTransition(self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.p_im)
        self.p_im.addTransition(ctrl.server_updated, self.p_im)
        self.p_im.addTransition(self.p_im.done, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.check_1)
        self.check_1.addTransition(ctrl.button['yes'].clicked, self.check_2)
        self.check_2.addTransition(ctrl.button['yes'].clicked, self.check_3)
        self.check_3.addTransition(ctrl.button['yes'].clicked, self.check_4)
        self.check_4.addTransition(ctrl.button['yes'].clicked, self.check_5)
        self.check_5.addTransition(ctrl.button['yes'].clicked, self.check_6)
        self.check_6.addTransition(ctrl.button['yes'].clicked, self.check_7)
        self.check_7.addTransition(ctrl.button['yes'].clicked, self.check_8)
        self.check_8.addTransition(ctrl.button['yes'].clicked, self.show_result)
        self.show_result.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back yes')
        ctrl.btp.kvt_breaking.tc1 = [-1.0] * 8
        ctrl.btp.kvt_breaking.tc2 = [-1.0] * 8
        ctrl.menu.current_menu.current_button.set_normal()


class ElBreaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ.".</p>')


class Speed60(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Выключите тумблер ">60 км/ч".</p>')


class Pim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Переведите ручку крана в отпускное положение</p>')
        if ctrl.manometer['p im'].get_value() <= 0.005:
            self.done.emit()


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "ВХОД" в положение "КУ"</p>')


class Check(QState):
    def __init__(self, stage: int, parent=None):
        super().__init__(parent=parent)
        self.stage = stage
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
        self.step: str = step[stage]

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Переведите ручку КУ 215 {self.step}.</p>' \
               f'<p>После того как давление в импульсной магистрали "Р им" стабилизируется (~10 с), ' \
               f'нажмите кнопку "ДА".</p>'
        ctrl.setText(text)

    def onExit(self, event: QEvent) -> None:
        ctrl.btp.kvt_breaking.tc1[self.stage] = ctrl.manometer['p tc1'].get_value()
        ctrl.btp.kvt_breaking.tc2[self.stage] = ctrl.manometer['p tc2'].get_value()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        ctrl.show_panel('текст')
        text = f'<p><table border="2" cellpadding="4" >' \
               f'<caption>Проверка ступеней торможения и отпуска при управлении ' \
               f'краном вспомогательного тормоза (КВТ)</caption>' \
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
        data = ctrl.btp.kvt_breaking
        stage = data.stage[row]
        rang = data.range_as_text(row)
        tc1 = data.tc1_as_text(row)
        tc2 = data.tc2_as_text(row)
        return f'<tr><td>   {stage}  </td><td>   {rang}   </td>' \
               f'<td align="center">   {tc1}   </td><td align="center">   {tc2}   </td></tr>'
