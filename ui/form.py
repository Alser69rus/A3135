from PyQt5 import QtWidgets


class MainForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(1024, 768)
        self.setWindowTitle('Стенд А3139')

        # todo 1 Create form
        # todo 1.1 Создать три панели и расположить их на форме вертикально
        self.vbox = QtWidgets.QVBoxLayout()
        self.manometers = QtWidgets.QWidget()
        self.manometers.setStyleSheet('QWidget{ background: yellow }')
        self.workspace = QtWidgets.QWidget()
        self.workspace.setStyleSheet('QWidget{ background: lightgreen }')
        self.btn_panel = QtWidgets.QWidget()
        self.btn_panel.setStyleSheet('QWidget{ background: blue }')
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.manometers)
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.btn_panel)
        # todo 1.2 Создать 7 панелей и расположить их горизонтально на центральном виджите
        self.hbox = QtWidgets.QHBoxLayout()
        self.menu = QtWidgets.QWidget()
        self.menu.setStyleSheet('QWidget{ background: red }')
        self.text = QtWidgets.QWidget()
        self.text.setStyleSheet('QWidget{ background: orange }')
        self.img = QtWidgets.QWidget()
        self.img.setStyleSheet('QWidget{ background: yellow }')
        self.graph = QtWidgets.QWidget()
        self.graph.setStyleSheet('QWidget{ background:  green}')
        self.settings = QtWidgets.QWidget()
        self.settings.setStyleSheet('QWidget{ background: cyan }')
        self.report_header = QtWidgets.QWidget()
        self.report_header.setStyleSheet('QWidget{ background: blue }')
        self.report = QtWidgets.QWidget()
        self.report.setStyleSheet('QWidget{ background: magenta }')
        self.workspace.setLayout(self.hbox)
        self.hbox.addWidget(self.menu)
        self.hbox.addWidget(self.text)
        self.hbox.addWidget(self.img)
        self.hbox.addWidget(self.graph)
        self.hbox.addWidget(self.settings)
        self.hbox.addWidget(self.report_header)
        self.hbox.addWidget(self.report)
        # todo 2 Создать меню
        # todo 2.1 Создать виджет кнопки
        # todo 2.2 Создать виджет одиночного меню
        # todo 2.3 Создать виджет с многостраничным меню
        # todo 2.4 напполнить меню для проекта и расположить его на форме
        # todo 2.5 сделать навигацию по меню
        # todo 3 Создать панель с кнопками
        # todo 3.1 Создать панель и расположить на ней несколько кнопок согласно ТЗ
        # todo 3.2 Сделать стиль для кнопок
        # todo 3.3 Сделать возможность включать и выключать кнопки панели
        # todo 4 создать панель манометров
        # todo 4.1 Создать круговую стрелку
        # todo 4.2 Создать круговой указатель
        # todo 4.3 создать круговую шкалу
        # todo 4.4 создать линейную шкалу
        # todo 4.5 создать несколько видов манометров (фабрику)
        # todo 4.6 расположить манометры на панели и положить на форму
        # todo 5 создать виджет с настройками
        # todo 5.1 расположить на форме индикатор состояния модулей ai и di
        # todo 5.2 создать настройку COM-порта
        # todo 5.3 создать настройку модулей
        # todo 5.4 создать настройку манометров
        # todo 5.5 создать настройку кнопок
        # todo 5.6 создать процедуру чтения и записи настроек в файл
        # todo 5.7 создать процедуру реинициализации модулей
        # todo 5.8 расположить виджет настроек на форме
        # todo 6 создать тесты для размеров формы
        # todo 7 Создать виджет заполнения формы испытания
