import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine, QTimer

from ui.main_form import MainForm
from controller.controller import Controller
from opc.server import Server

from modules.menu_state import MenuState

import logging

# logging.basicConfig(level=logging.DEBUG,format='%(name)s %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.server = Server()
        self.form = MainForm(self.server)
        self.stm = QStateMachine()
        self.controller = Controller(server=self.server,
                                     form=self.form,
                                     stm=self.stm)

        self.controller.show_panel('меню')
        self.form.show()
        self.controller.text.setText('Hello')
        self.controller.show_menu('Главное')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    logging.debug(f'window size: {main.form.width()}x{main.form.height()}')

    sys.exit(app.exec_())
