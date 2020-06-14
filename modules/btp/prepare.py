from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller


class Prepare(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common: Common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        menu = ctrl.menu.menu['БТП 020']
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu_state.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.ppm = common.Ppm(self)
        self.install_ku = InstallKU(self)
        self.ku_215 = common.KU215(self)
        self.pim = common.Pim(self)
        self.tank = common.Tank(state='СБРОС', parent=self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.set_bto = SetBTO(self)
        self.enter = common.Enter(state='ВР', parent=self)
        self.connect_btp = ConnectBTP(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.install_ku)
        self.install_ku.addTransition(ctrl.button['yes'].clicked, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.tank)
        self.tank.addTransition(ctrl.switch_with_neutral['tank'].state_two, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.set_bto)
        self.set_bto.addTransition(ctrl.button['yes'].clicked, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_one, self.connect_btp)
        self.connect_btp.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')


class InstallKU(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p><font color="red">ВНИМАНИЕ! БТО испытывается с исправным КУ 215.</font></p>' \
               f'<p>Установите КУ 215 на прижим, включите пневмотумблер "ПРИЖИМ КУ 215".</p>' \
               f'<p><br>Для продолжения нажмите "ДА"</p>'
        ctrl.setText(text)


class SetBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Установите БТО на стойку.</p>' \
               f'<p>Установите тумблером "50 В - 100 В" напряжение, соответствующее рабочему напряжению БТО.</p>' \
               f'<p>Подключите электрические шлейфы от стенда к БТО.</p><p>Подключите пневматические рукава к БТО.</p>' \
               f' <p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)


class ConnectBTP(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Включите пневмотумблер "БТП К СТЕНДУ".</p>' \
               f'<p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)
        ctrl.menu.current_menu.current_button.set_success()
