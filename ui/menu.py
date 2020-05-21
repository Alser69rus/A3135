from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QObject
from enum import Enum, auto
from typing import List, Optional

ANIMATE_CLICK_DELAY=50

class ButtonState(Enum):
    NORMAL = auto()
    SUCCESS = auto()
    FAIL = auto()


class ButtonBorder(Enum):
    NORMAL = auto()
    SELECTED = auto()


class ButtonStyle:
    def __init__(self):
        self.color = {
            ButtonState.NORMAL: 'rgba(10,10,10,0%)',
            ButtonState.SUCCESS: 'rgba(0,200,0,10%)',
            ButtonState.FAIL: 'rgba(200,0,0,10%)',
        }
        self.pressed: str = 'rgba(30,0,0,30%)'

        self.border = {
            ButtonBorder.NORMAL: 'none',
            ButtonBorder.SELECTED: 'solid',
        }

        self.icon = {
            ButtonState.NORMAL: QIcon('img\\empty.png'),
            ButtonState.SUCCESS: QIcon('img\\success.png'),
            ButtonState.FAIL: QIcon('img\\fail.png'),
        }

        self.state: ButtonState = ButtonState.NORMAL
        self.selected: bool = False

    def current(self) -> (str, QIcon):
        background_color: str = self.color[self.state]
        border: str = self.border[ButtonBorder.SELECTED] if self.selected else self.border[ButtonBorder.NORMAL]
        icon = self.icon[self.state]

        style: str = f'QPushButton' \
                     f'{{' \
                     f'border:2px;' \
                     f'border-radius:8px;' \
                     f'border-color:black;' \
                     f'text-align:left;' \
                     f'padding: 8px;' \
                     f'background-color:{background_color};' \
                     f'border-style:{border}' \
                     f'}}' \
                     f' ' \
                     f'QPushButton:pressed' \
                     f'{{' \
                     f'background-color:{self.pressed}' \
                     f'}}'
        return style, icon


class MenuButton(QPushButton):
    mouse_entry = pyqtSignal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setFlat(True)
        self.setFont(QFont('Segoi Ui', 16))
        self.setMouseTracking(True)
        self.setText(text)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIconSize(QSize(32, 32))

        self.button_style = ButtonStyle()
        self.button_state = ButtonState
        self._state: ButtonState = ButtonState.NORMAL
        self._selected: bool = False
        self.set_normal()

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value
        self.button_style.selected = value
        self.set_style()

    @property
    def state(self) -> ButtonState:
        return self._state

    @state.setter
    def state(self, value: ButtonState):
        self._state = value
        self.button_style.state = value
        self.set_style()

    def set_normal(self):
        self.state = ButtonState.NORMAL

    def set_success(self):
        self.state = ButtonState.SUCCESS

    def set_fail(self):
        self.state = ButtonState.FAIL

    def set_style(self):
        style, icon = self.button_style.current()
        self.setStyleSheet(style)
        self.setIcon(icon)

    def enterEvent(self, *args, **kwargs):
        self.mouse_entry.emit()


class Menu(QWidget):
    button_clicked = pyqtSignal()

    def __init__(self, caption: str, parent=None):
        super().__init__(parent=parent)
        self.caption = QLabel()
        self.caption.setFont(QFont('Segoi Ui', 32))
        self.caption.setAlignment(Qt.AlignCenter)
        self.caption.setText(caption)

        self.buttons: List[MenuButton] = []
        self.buttons_widget = QWidget()
        self.btn_box = QVBoxLayout()
        self.buttons_widget.setLayout(self.btn_box)

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.caption)
        self.vbox.addSpacing(20)
        self.vbox.addWidget(self.buttons_widget)
        self.vbox.addStretch(1)

        self.button: Optional[MenuButton] = None

        self.button_style = ButtonStyle()

        self.active: bool = True

    def add_button(self, text: str) -> MenuButton:
        button = MenuButton(text)
        button.button_style = self.button_style
        button.mouse_entry.connect(self.on_button_entry)
        button.clicked.connect(self.button_clicked)
        self.buttons.append(button)
        self.btn_box.addWidget(button)
        if self.button is None:
            self.button = button
            button.selected = True
        return button

    @pyqtSlot()
    def on_button_entry(self):
        self.select(self.sender())

    def reset(self):
        for button in self.buttons:
            button.set_normal()
            button.selected = False

        if self.buttons:
            self.button = self.buttons[0]
            self.button.selected = True

    def select(self, button: QObject):
        if not button.isEnabled(): return
        if not (self.button is None):
            self.button.selected = False
        self.button = button
        self.button.selected = True

    def next_element(self, button: MenuButton):
        if not self.buttons: return None
        if button is None: return self.buttons[0]
        i = self.buttons.index(button)
        i = (i + 1) if i < len(self.buttons) - 1 else 0
        btn: MenuButton = self.buttons[i]
        if btn.isVisible() and btn.isEnabled():
            return btn
        return self.next_element(btn)

    def previous_element(self, button: MenuButton):
        if not self.buttons: return None
        if button is None: return self.buttons[0]
        i = self.buttons.index(button)
        i = (i - 1) if i > 0 else len(self.buttons) - 1
        btn = self.buttons[i]
        if btn.isVisible() and btn.isEnabled():
            return btn
        return self.previous_element(btn)

    @pyqtSlot()
    def on_ok_click(self):
        if not self.active: return
        if self.button is None: return
        self.button.animateClick(ANIMATE_CLICK_DELAY)

    @pyqtSlot()
    def on_back_click(self):
        pass

    @pyqtSlot()
    def on_up_click(self):
        if not self.active: return
        self.select(self.previous_element(self.button))

    @pyqtSlot()
    def on_down_click(self):
        if not self.active: return
        self.select(self.next_element(self.button))


class MenuWidget(QWidget):
    button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.menus: List[Menu] = []
        self.menu: Optional[Menu] = None
        self.button_style: ButtonStyle = ButtonStyle()

        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        self.active: bool = True

    def add_menu(self, caption: str) -> Menu:
        menu = Menu(caption)
        menu.button_style = self.button_style
        menu.button_clicked.connect(self.button_clicked)
        self.menus.append(menu)
        self.layout.addWidget(menu)
        if self.menu is None:
            self.show_menu(menu)
        return menu

    def show_menu(self, menu: Menu):
        self.menu = menu
        self.layout.setCurrentWidget(menu)

    @pyqtSlot()
    def on_ok_click(self):
        if not self.active: return
        if self.menu is None: return
        self.menu.on_ok_click()

    @pyqtSlot()
    def on_back_click(self):
        if not self.active: return
        if self.menu is None: return
        self.menu.on_back_click()

    @pyqtSlot()
    def on_up_click(self):
        if not self.active: return
        if self.menu is None: return
        self.menu.on_up_click()

    @pyqtSlot()
    def on_down_click(self):
        if not self.active: return
        if self.menu is None: return
        self.menu.on_down_click()
