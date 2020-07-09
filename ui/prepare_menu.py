from PyQt5.QtWidgets import QDialog, QInputDialog,QPushButton
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QSettings
from PyQt5.QtGui import QFont
from ui.menu import MenuWidget, Menu, MenuButton


class PrepareMenu(QObject):
    def __init__(self, widget: MenuWidget, parent=None):
        super().__init__(parent=parent)
        self.widget = widget
        menu: Menu = widget.add_menu('Подготовка к испытанию')
        self.button_names_1 = ['Заводской номер: ',
                               'Дата изготовления: ',
                               'Номер тепловоза: ',
                               'Номер секции: ',
                               ]
        self.button_names_2 = ['Испытание провел: ',
                               'Испытание проверил: ', ]
        self.button_names = self.button_names_1 + self.button_names_2

        for name in self.button_names:
            button: MenuButton = menu.add_button(name)
            button.clicked.connect(self.on_button_click)
            button.name = name
            button.data = ''

        self.done = menu.add_button('Приступить к испытанию')
        self.menu: Menu = menu
        self.reset()

    def reset(self):
        for name in self.button_names_1:
            self.menu.button[name].data = ''
        self.update_fields()

    def update_fields(self):
        for name in self.button_names:
            button = self.menu.button[name]
            button.setText(f'{name} {button.data}')

        all_fields_are_filled = all([self.menu.button[name].data for name in self.button_names])

        if all_fields_are_filled:
            self.menu.button['Приступить к испытанию'].setEnabled(True)
        else:
            self.menu.button['Приступить к испытанию'].setEnabled(False)

    @pyqtSlot()
    def on_button_click(self):
        button = self.sender()

        employees = QSettings('settings.ini', QSettings.IniFormat)
        employees.setIniCodec('UTF-8')
        employees = employees.value('employees')

        dialog = QInputDialog()
        dialog.setFont(QFont('Segoi Ui', 16))
        dialog.setWindowTitle('Ввод значения')
        dialog.setOkButtonText('Принять')
        dialog.setCancelButtonText('Отмена')
        dialog.setTextValue(button.data)

        if button in [self.menu.button['Испытание провел: '],
                      self.menu.button['Испытание проверил: ']]:
            dialog.setComboBoxItems(employees)
            dialog.setComboBoxEditable(True)

        dialog.setLabelText(button.name)
        result = dialog.exec()

        if result == QDialog.Accepted:
            button.data = dialog.textValue()
            self.update_fields()

    def get_data_fields(self):
        return list(self.menu.button[name].data for name in self.button_names)
