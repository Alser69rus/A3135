import logging
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine

from controller.controller import Controller
from modules.menu import MenuState
from opc.server import Server
from ui.main_form import MainForm

logging.basicConfig(level=logging.WARNING, format='%(name)s %(asctime)s - %(levelname)s - %(message)s')


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


def already_run() -> bool:
    import psutil
    import os
    from collections import Counter

    cwd = os.getcwd()
    exe = Counter()

    pids = psutil.pids()
    for pid in pids:
        try:
            proc = psutil.Process(pid).as_dict(['cwd', 'exe'])
            if proc['cwd'] == cwd: exe[proc['exe']] += 1
        except Exception:
            pass
    return exe.most_common(1)[0][1] > 1


if __name__ == '__main__':

    if already_run(): sys.exit('Программа уже запущена')

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
