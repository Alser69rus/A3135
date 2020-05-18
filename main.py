import sys
from PyQt5 import QtCore, QtWidgets

import logging

logging.basicConfig(level=logging.DEBUG)

from ui.main_form import MainForm
from controller.controller import Controller


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.form = MainForm()
        self.stm = QtCore.QStateMachine()

        self.controller = Controller()
        self.controller.connect_button_panel(self.form.btn_panel)
        self.form.keyPressEvent = self.controller.keyPressEvent

    def start(self):
        self.form.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.start()

    sys.exit(app.exec_())
