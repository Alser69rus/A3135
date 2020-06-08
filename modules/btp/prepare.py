from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller


class Prepare(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        menu = ctrl.menu.menu['БТП 020']
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu_state.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.check_pim = CheckPim(self)
        self.check_zam_el_torm = CheckZamElTorm(self)
        self.check_speed_60 = CheckSpeed60(self)
        self.set_bto = SetBTO(self)
        self.enter_vr = EnterVr(self)
        self.btp_to_stand = BtpToStand(self)

        self.setInitialState(self.start)
        self.start.addTransition(ctrl.server_updated, self.start)
        self.start.addTransition(self.start.done, self.check_pim)
        self.check_pim.addTransition(ctrl.server_updated, self.check_pim)
        self.check_pim.addTransition(self.check_pim.done, self.check_zam_el_torm)
        self.check_zam_el_torm.addTransition(ctrl.server_updated, self.check_zam_el_torm)
        self.check_zam_el_torm.addTransition(self.check_zam_el_torm.done, self.check_speed_60)
        self.check_speed_60.addTransition(ctrl.server_updated, self.check_speed_60)
        self.check_speed_60.addTransition(self.check_speed_60.done, self.set_bto)
        self.set_bto.addTransition(ctrl.button['yes'].clicked, self.enter_vr)
        self.enter_vr.addTransition(ctrl.server_updated, self.enter_vr)
        self.enter_vr.addTransition(self.enter_vr.done, self.btp_to_stand)
        self.btp_to_stand.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')
        text = f'<p><font color="red">ВНИМАНИЕ! БТО испытывается с исправным КУ 215.</font></p>' \
               f'<p>Установите КУ 215 на прижим, включите пневмотумблер "ПРИЖИМ КУ 215".</p>' \
               f'<p>Включите тумблер "КУ 215".</p>'

        ctrl.setText(text)
        if ctrl.switch['ku 215'].get_value():
            self.done.emit()


class CheckPim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Необходимо сбросить до нуля давление в импульсной магистрали. ' \
               f'Для этого переведите ручку крана в отпускное положение.</p>' \
               f'<p>Вклучите тумблер "НАКОП. РЕЗ." в положение "СБРОС".</p>'

        ctrl.setText(text)
        if ctrl.manometer['p im'].get_value() < 0.005:
            self.done.emit()


class CheckZamElTorm(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."</p>'
        ctrl.setText(text)
        if not ctrl.switch['el. braking'].get_value():
            self.done.emit()


class CheckSpeed60(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Выключите тумблер "> 60 км/ч"</p>'
        ctrl.setText(text)
        if not ctrl.switch['>60 km/h'].get_value():
            self.done.emit()


class SetBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Установите БТО на стойку.</p>' \
               f'<p>Установите тумблером "50 В - 100 В" напряжение, соответствующее рабочему напряжению БТО.</p>' \
               f'<p>Подключите электрические шлейфы от стенда к БТО.</p><p>Подключите пневматические рукова к БТО.</p>' \
               f' <p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)


class EnterVr(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Включите тумблер "ВХОД" в положение "ВР".</p>'
        ctrl.setText(text)
        if ctrl.switch_with_neutral['enter'].value_sa_text() == 'ВР':
            self.done.emit()


class BtpToStand(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Включите пневмотумблер "БТП К СТЕНДУ".</p>' \
               f'<p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)
        ctrl.menu.current_menu.current_button.set_success()
