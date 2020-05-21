from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from ui.button_panel import ButtonPanel
from ui.workspace import Workspace
from ui.manometers_panel import Manometers



class MainForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(1024, 768)
        self.setWindowTitle('Стенд А3139')

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.manometers = Manometers()
        self.workspace = Workspace()
        self.btn_panel = ButtonPanel()

        self.setLayout(self.vbox)
        self.vbox.addWidget(self.manometers)
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.btn_panel)

        # todo 2 Создать меню
        # todo 2.1 Создать виджет кнопки
        # todo 2.2 Создать виджет одиночного меню
        # todo 2.3 Создать виджет с многостраничным меню
        # todo 2.4 напполнить меню для проекта и расположить его на форме
        # todo 2.5 сделать навигацию по меню

        # todo 5 создать виджет с настройками
        # todo 5.1 расположить на форме индикатор состояния модулей ai и di
        # todo 5.2 создать настройку COM-порта
        # todo 5.3 создать настройку модулей
        # todo 5.4 создать настройку манометров
        # todo 5.5 создать настройку кнопок
        # todo 5.6 создать процедуру чтения и записи настроек в файл
        # todo 5.7 создать процедуру реинициализации модулей
        # todo 5.8 расположить виджет настроек на форме

        # todo 7 Создать виджет заполнения формы испытания
        # todo 8Создать виджет отчета

    @pyqtSlot(str)
    def show_panel(self, value: str):
        available_panel = {
            'манометры': self.manometers,
            'меню': self.workspace.menu,
            'текст': self.workspace.text,
            'картинка': self.workspace.img,
            'график': self.workspace.graph,
            'настройки': self.workspace.settings,
            'заголовок': self.workspace.report_header,
            'отчет': self.workspace.report,
        }
        for panel in available_panel.keys():
            available_panel[panel].setVisible(panel in value)
