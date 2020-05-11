import sys
from PyQt5 import QtCore, QtWidgets

import logging

logging.basicConfig(level=logging.DEBUG)

from ui import form


class Main:
    def __init__(self):
        print('Стенд А3139')
        print('(c) ПКБ ЦТ, 2020')

        self.form = form.MainForm()
        logging.debug('main form load ok')

        self.stm = QtCore.QStateMachine()

    def start(self):
        self.form.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.start()


    sys.exit(app.exec_())
