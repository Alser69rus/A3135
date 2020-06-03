import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine, QTimer

from ui.main_form import MainForm
from ui.control_window import ControlWindow
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

        self.form = MainForm()
        self.stm = QStateMachine()
        self.server = Server()
        self.controller = Controller()

        self.controller.connect_form(self.form)
        self.controller.connect_server(self.server)
        self.controller.connect_state_machine(self.stm)

        self.controller.connect_manometers()
        self.controller.connect_di_buttons()

        self.controller.show_panel('текст манометры')
        self.form.show()
        self.controller.text.setText('Hello')
        self.controller.show_menu('Главное')

        self.ctrl_win = ControlWindow()
        self.controller.connect_control_window(self.ctrl_win)
        self.ctrl_win.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    logging.debug(f'window size: {main.form.width()}x{main.form.height()}')

    sys.exit(app.exec_())
