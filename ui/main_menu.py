from PyQt5.QtCore import pyqtSlot
from ui.menu import MenuWidget


class MainMenu(MenuWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        menu = self.add_menu('main', 'Главное меню')
        menu.add_button('btp 020', 'Испытание БТП 020')
        menu.add_button('rd 042', 'Испытание РД 042')
        menu.add_button('ku 215', 'Испытание КУ 215')
        menu.add_button('keb 208', 'Испытание КЭБ 208')
        menu.add_button('Выход')

        menu = self.add_menu('btp 020', 'Программа испытания БТП 020')
        menu.add_button('prepare','Подготовка к испытанию')
        menu.add_button('torm_auto','Проверка ступенчатого торможения и отпуска при действии автоматического тормоза')
