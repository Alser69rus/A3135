from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from typing import Dict, List
from opc.opc import TwoStateDiscreteType
from functools import partial

ANIMATE_CLICK_DELAY = 50


class ButtonPanel(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.NoFocus)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumHeight(40)
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.button_icons: Dict[str, QIcon] = {
            'back': QIcon('img\\back.png'),
            'up': QIcon('img\\up.png'),
            'down': QIcon('img\\down.png'),
            'yes': QIcon('img\\yes.png'),
            'no': QIcon('img\\no.png'),
        }

        self.button: Dict[str, ButtonWidget] = {}
        for key in self.button_icons.keys():
            button = ButtonWidget(button=server.button[key], icon=self.button_icons[key])
            self.button[key] = button
            self.hbox.addWidget(button)


class ButtonWidget(QPushButton):
    def __init__(self, button: TwoStateDiscreteType, icon: QIcon, parent=None):
        super().__init__(parent=parent)
        button.clicked.connect(partial(self.animateClick, ANIMATE_CLICK_DELAY))
        self.setText(button.name)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIcon(icon)
        self.setStyleSheet(
            f'QPushButton'
            f'{{'
            f'border:2px;'
            f'border-radius:8px;'
            f'border-color:black;'
            f'text-align:center;'
            f'padding: 4px;'
            f'background-color:rgba(10,10,10,10%);'
            f'border-style:none;'
            f'font:20px "Segoi UI";'
            f'min-width:80px;'
            f'icon-size: 32px 32px'
            f'}}'
            f' QPushButton:pressed'
            f'{{'
            f'background-color:rgba(30,0,0,30%)'
            f'}}'
        )
