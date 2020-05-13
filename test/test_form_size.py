import unittest
from PyQt5 import QtWidgets, QtTest
from ui import main_form


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = QtWidgets.QApplication([])
        self.form = main_form.MainForm()
        self.form.show()

    def test_width(self):
        self.assertEqual(self.form.width(), 1024, msg='form width')

    def test_height(self):
        self.assertEqual(self.form.height(), 768, msg='form height')


if __name__ == '__main__':
    unittest.main()
