from PyQt5.QtCore import pyqtSlot
from ui.menu import MenuWidget


class MainMenu(MenuWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main = self.add_menu('Главное меню')
        self.main.btn1 = self.main.add_button('Первая кнопка')
        self.main.btn2 = self.main.add_button('Вторая кнопка')
        self.main.btn3 = self.main.add_button('Третья кнопка')
        self.main.btn4 = self.main.add_button('Четвертая кнопка')


