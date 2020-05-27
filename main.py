import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine

import logging

# logging.basicConfig(level=logging.DEBUG,format='%(name)s %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO)

from ui.main_form import MainForm
from controller.controller import Controller
from opc.opc import Opc


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.opc = Opc()

        # self.opc.server.start()

        self.form = MainForm()
        self.form.show_panel('меню, манометры')

        self.stm = QStateMachine()

        self.controller = Controller(form=self.form, state_machine=self.stm)

        self.form.show()
        self.controller.text.setText('Hello')

        self.opc.worker.ai.pin[0].value_changed.connect(self.form.manometers.p_pm.set_value)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    sys.exit(app.exec_())
