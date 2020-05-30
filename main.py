import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine, QTimer

from ui.main_form import MainForm
from controller.controller import Controller
from opc.server import Server

from modules.menu import MenuState

import logging

# logging.basicConfig(level=logging.DEBUG,format='%(name)s %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.form = MainForm()
        self.stm = QStateMachine()
        self.server = Server()
        self.controller = Controller()

        self.controller.connect_form(self.form)
        self.controller.connect_server(self.server)
        self.controller.connect_state_machine(self.stm)

        self.controller.connect_manometers()
        self.controller.connect_di_buttons()

        self.form.show_panel('меню')
        self.form.show()
        self.controller.text.setText('Hello')
        self.controller.menu.show_menu('Подготовка к испытанию')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    logging.debug(f'window size: {main.form.width()}x{main.form.height()}')

    sys.exit(app.exec_())
