from PyQt5 import QtWidgets, QtGui


class ButtonPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.back = QtWidgets.QPushButton('Возврат')
        self.up = QtWidgets.QPushButton('Вверх')
        self.down = QtWidgets.QPushButton('Вниз')
        self.yes = QtWidgets.QPushButton('Да')
        self.no = QtWidgets.QPushButton('Нет')

        self.back.setIcon(QtGui.QIcon('img\\back.png'))
        self.up.setIcon(QtGui.QIcon('img\\up.png'))
        self.down.setIcon(QtGui.QIcon('img\\down.png'))
        self.yes.setIcon(QtGui.QIcon('img\\yes.png'))
        self.no.setIcon(QtGui.QIcon('img\\no.png'))
        
        self.hbox = QtWidgets.QHBoxLayout()
        self.setLayout(self.hbox)
        self.hbox.addWidget(self.back)
        self.hbox.addWidget(self.up)
        self.hbox.addWidget(self.down)
        self.hbox.addWidget(self.yes)
        self.hbox.addWidget(self.no)

        self.style_sheet = 'QPushButton' \
                           '{' \
                           'border:2px;' \
                           'border-radius:8px;' \
                           'border-color:black;' \
                           'text-align:center;' \
                           'padding: 4px;' \
                           'background-color:rgba(10,10,10,10%);' \
                           'border-style:none;' \
                           'font:20px "Segoi UI";' \
                           'min-width:80px;' \
                           'icon-size: 32px 32px' \
                           '}' \
                           ' QPushButton:pressed' \
                           '{' \
                           'background-color:rgba(30,0,0,30%)' \
                           '}'

        self.setStyleSheet(self.style_sheet)

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.Fixed)
        self.size().setHeight(40)
