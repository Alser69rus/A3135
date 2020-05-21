import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QStateMachine
from PyQt5.QtGui import QPixmap

import logging

logging.basicConfig(level=logging.DEBUG)

from ui.main_form import MainForm
from controller.controller import Controller


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.form = MainForm()
        self.form.show_panel('текст график манометры')

        self.stm = QStateMachine()

        self.controller = Controller(form=self.form, state_machine=self.stm)

        self.form.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    sys.exit(app.exec_())
