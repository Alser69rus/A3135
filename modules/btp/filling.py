from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller
p = None


class Filling(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Время наполненя ТЦ'].clicked, self)

        self.start = Start(self)
        self.pim = Pim(self)
'''



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
'''



        # self.start = Start(self)
        # self.el_breaking = ElBreaking(self)
        # self.speed_60 = Speed60(self)
        # self.p_im = Pim(self)
        # self.enter = Enter(self)
        # self.wait = Wait(self)
        # self.measure = Measure(self)
        #
        # self.setInitialState(self.start)
        # self.start.addTransition(self.el_breaking)
        # self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        # self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.p_im)
        # self.p_im.addTransition(ctrl.server_updated, self.p_im)
        # self.p_im.addTransition(self.p_im.done, self.enter)
        # self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_two, self.wait)
        # self.wait.addTransition(ctrl.server_updated, self.wait)
        # self.wait.addTransition(self.wait.done, self.measure)
        # self.measure.addTransition(ctrl.server_updated, self.measure)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')
        ctrl.btp.kvt_breaking.tc1 = -1.0
        ctrl.menu.current_menu.current_button.set_normal()


class ElBreaking(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."')


class Speed60(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Выключите тумблер ">60 км/ч".')


class Pim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Переведите ручку крана в отпускное положение.')
        if ctrl.manometer['p im'].get_value() <= 0.005:
            self.done.emit()


class Enter(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Включите тумблер "ВХОД" в  положение "КУ".')


class Wait(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        global p

        ctrl.setText(f'Переведите ручку КУ 215 в четвертое положение за один прием.')
        ctrl.btp.filing.set_t1()
        manometers = ['p im', 'p tc1', 'p tc2']
        p = [ctrl.manometer[key].get_value() > 0.005 for key in manometers]
        if any(p):
            self.done.emit()
            ctrl.show_panel('манометры график')


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        tc1 = (ctrl.manometer['p tc1'].get_value(), ctrl.manometer['p tc1'].name, 'm')
        tc2 = (ctrl.manometer['p tc2'].get_value(), ctrl.manometer['p tc2'].name, 'c')
        ctrl.btp.filing.set_t2(tc1[0], tc2[0])
        t = ctrl.btp.filing.t_arr
        p1 = ctrl.btp.filing.tc1
        p2 = ctrl.btp.filing.tc2
        ctrl.graph.ptc1.setData(x=t, y=p1)
        ctrl.graph.ptc2.setData(x=t, y=p2)
