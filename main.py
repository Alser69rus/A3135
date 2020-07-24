import logging
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine

from controller.controller import Controller
from modules.menu import MenuState
from opc.server import Server
from ui.main_form import MainForm

logging.basicConfig(level=logging.DEBUG, format='%(name)s %(asctime)s - %(levelname)s - %(message)s')


# logging.basicConfig(level=logging.WARNING

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
        self.controller.text.setText('Hello')
        self.controller.show_menu('Главное меню')
        self.form.showMaximized()

        self.menu_state = MenuState(self.controller)
        self.stm.setInitialState(self.menu_state)
        self.stm.start()


if __name__ == '__main__':
    import psutil
    import os

    running_programm = 0
    cwd = os.getcwd()

    pids = psutil.pids()
    for pid in pids:
        try:
            proc = psutil.Process(pid).as_dict(['name', 'cwd', 'exe'])
            if proc['cwd'] == cwd: print('0', proc['name'], proc['exe'])
        except Exception:
            pass

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
