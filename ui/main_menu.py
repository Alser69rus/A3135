from ui.menu import MenuWidget
from ui.prepare_menu import PrepareMenu


class MainMenu(MenuWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        menu = self.add_menu('Главное меню')
        self.main_btp = menu.add_button('БТП 020','Испытание БТП 020')
        self.main_btp.setVisible(False)
        self.main_rd = menu.add_button('РД 042','Испытание РД 042')
        self.main_ku = menu.add_button('КУ 215','Испытание КУ 215')
        self.main_keb = menu.add_button('КЭБ 208', 'Испытание КЭБ 208')
        self.main_kp = menu.add_button('КП 106', 'Испытание КП 106')
        self.main_exit = menu.add_button('Выход')

        menu = self.add_menu('БТП 020', 'Программа испытания БТП 020')
        menu.add_button('Подготовка', 'Подготовка к испытанию')
        menu.add_button('торможение автоматическое',
                        'Проверка ступенчатого торможения и отпуска при действии автоматического \nтормоза')
        menu.add_button('торможение КВТ',
                        'Проверка ступенчатого торможения и отпуска при управлении краном \nвспомогательного тормоза (КВТ)')
        menu.add_button('Время наполненя ТЦ',
                        'Проверка времени наполнения ТЦ при управлении краном вспомогательного \nтормоза (КВТ)')
        menu.add_button('Герметичность', 'Проверка герметичности мест соединений')
        menu.add_button('Время снижения',
                        'Проверка времени снижения давления в ТЦ при управлении краном \nвспомогательного '
                        'тормоза (КВТ)')
        menu.add_button('Замещение торможения', 'Проверка работы БТО при замещении электрического торможения')
        menu.add_button('Повышенная скорость', 'Проверка работы БТО при движении на повышенных скоростях')
        menu.add_button('Завершение', 'Завершение испытаний')

        menu = self.add_menu('РД 042', 'Программа испытания РД 042')
        menu.add_button('Подготовка', 'Подготовка к испытанию')
        menu.add_button('Герметичность соединений', 'Проверка плотности мест соединений')
        menu.add_button('Герметичность клапана', 'Проверка плотности атмосферного клапана')
        menu.add_button('Время наполнения', 'Проверка времени наполнения ТЦ (торможение)')
        menu.add_button('Поддержание давления',
                        'Проверка автоматического поддержания установившегося зарядного давления \n'
                        '(чувствительность) в ТЦ при создании утечки из него')
        menu.add_button('Время отпуска', 'Проверка времени снижения давления в ТЦ (отпуск)')
        menu.add_button('Завершение', 'Завершение испытаний')

        menu = self.add_menu('КУ 215', 'Программа испытания КУ 215')
        menu.add_button('Подготовка', 'Подготовка к испытанию')
        menu.add_button('Герметичность соединений', 'Проверка плотности мест соединений')
        menu.add_button('Герметичность клапана', 'Проверка плотности атмосферного клапана')
        menu.add_button('Ступени торможения', 'Проверка давлений в импульсной магистрали на ступенях торможения')
        menu.add_button('Утечка',
                        'Проверка величины снижения давления в импульсной магистрали при создании \nутечки из нее')
        menu.add_button('Время наполнения', 'Проверка времени наполнения импульсной магистрали')
        menu.add_button('Снижение давления', 'Проверка времени снижения давления в импульсной магистрали')
        menu.add_button('Завершение', 'Завершение испытаний')

        menu = self.add_menu('КЭБ 208', 'Программа испытания КЭБ 208')
        menu.add_button('Подготовка к испытанию')
        menu.add_button('Время торможения', 'Проверка времени наполнения ТЦ (торможение)')
        menu.add_button('Герметичность соединений', 'Проверка плотности мест соединений')
        menu.add_button('Время отпуска', 'Проверка времени снижения давления в ТЦ (отпуск)')
        menu.add_button('Завершение', 'Завершение испытаний')

        menu = self.add_menu('КП 106', 'Программа испытания КП 106')
        menu.add_button('Подготовка к испытанию')
        menu.add_button('Испытание 1', 'Испытание 1')
        menu.add_button('Испытание 2', 'Испытание 2')
        menu.add_button('Завершение', 'Завершение испытаний')

        self.prepare_menu = PrepareMenu(self)

    def reset_prepare(self):
        self.prepare_menu.reset()
