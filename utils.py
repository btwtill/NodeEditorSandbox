import traceback

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def dumpException(e):
    print("EXEPTION", e)
    traceback.print_tb(e.__traceback__)

def loadStyleSheet(filename):

    print("loading Style from Path: ", filename)

    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)

    stylesheet = file.readAll()

    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

def loadStyleSheets(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding = 'utf-8')
    QApplication.instance().setStyleSheet(res)