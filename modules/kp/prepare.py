from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller

ctrl: Controller


class Prepare(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КП 106']
        parent.menu.addTransition(menu.button['Подготовка к испытанию'].clicked, self)

        self.start = Start(self)
        self.install = Install(self)
        self.tc820 = Tc820(self)
        self.rdkp = Rdkp(self)
        self.km = Km(self)
        self.ptm = Ptm(self)
        self.set_ptm = SetPtm(self)
        self.kp106 = Kp106(self)
        self.rd042 = Rd042(self)
        self.upr_rd042 = UprRd042(self)
        self.pupr = Pupr(self)
        self.set_pupr = SetPupr(self)
        self.enable_menu = EnableMenu(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.install)
        self.install.addTransition(ctrl.button['yes'].clicked, self.tc820)
        self.tc820.addTransition(ctrl.switch['tc 820'].high_value, self.rdkp)
        self.rdkp.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_two, self.km)
        self.km.addTransition(ctrl.switch_with_neutral['km'].state_one, self.ptm)
        self.ptm.addTransition(self.ptm.success, self.kp106)
        self.ptm.addTransition(self.ptm.fail, self.set_ptm)
        self.set_ptm.addTransition(ctrl.server_updated, self.set_ptm)
        self.set_ptm.addTransition(ctrl.button['yes'].clicked, self.kp106)
        self.kp106.addTransition(ctrl.switch['kp 106'].high_value, self.rd042)
        self.rd042.addTransition(ctrl.switch['rd 042'].high_value, self.upr_rd042)
        self.upr_rd042.addTransition(ctrl.switch['upr rd 042'].high_value, self.pupr)
        self.pupr.addTransition(self.pupr.success, self.enable_menu)
        self.pupr.addTransition(self.pupr.fail, self.set_pupr)
        self.set_pupr.addTransition(ctrl.server_updated, self.set_pupr)
        self.set_pupr.addTransition(ctrl.button['yes'].clicked, self.enable_menu)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back yes')
        ctrl.normal()


class Install(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p><font color="red">ВНИМАНИЕ! КП 106 испытывается с исправным РД 042.</font></p>'
                     f'<p><br>Установите РД 042 на прижим и включите пневмотумблер "ПРИЖИМ РД 042".</p>'
                     f'<p>Установите КП 106 на прижим и включите пневмотумблер "ПРИЖИМ КП 106".</p>'
                     f'<p><br>Для продолжения нажмите "ДА".</p>')


class Tc820(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText(f'<p>Включите тумблер "ТЦ2 8 л - 20 л" в положение "20 л".</p>')


class Rdkp(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "КП 106".</p>')


class Km(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Включите тумблер "КМ" в положение "ОТПУСК".</p>')


class Ptm(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        if 0.52 <= ctrl.manometer['p tm'].get_value() <= 0.55:
            self.success.emit()
        else:
            self.fail.emit()


class SetPtm(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Установите давление в магистрали ТМ в пределах 0,52-0,55 МПа.</p>'
                     f'<p><br>Для продолжения нажите "ДА".</p>')
        if 0.52 <= ctrl.manometer['p tm'].get_value() <= 0.55:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class Kp106(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "КП 106".')


class Rd042(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "РД 042".')


class UprRd042(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УПР. РД 042".')


class Pupr(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.40:
            self.success.emit()
        else:
            self.fail.emit()


class SetPupr(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'<p>Установите давление управления РД/СД в пределах 0,38-0,40 МПа.</p>'
                     f'<p><br>Для продолжения нажите "ДА".</p>')
        if 0.38 <= ctrl.manometer['p upr'].get_value() <= 0.40:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class EnableMenu(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        menu = ctrl.menu.menu['КП 106']
        buttons = [
            'Испытание',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(True)
