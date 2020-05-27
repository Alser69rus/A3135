import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine

from ui.main_form import MainForm
from controller.controller import Controller
from opc.server import Server

import logging

# logging.basicConfig(level=logging.DEBUG,format='%(name)s %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO)


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.form = MainForm()
        self.form.show_panel('меню')

        self.stm = QStateMachine()
        self.server = Server()

        self.controller = Controller(form=self.form,
                                     state_machine=self.stm,
                                     server=self.server)

        self.form.show()
        self.controller.text.setText('Hello')
        self.controller.menu.show_menu('btp 020')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    sys.exit(app.exec_())
