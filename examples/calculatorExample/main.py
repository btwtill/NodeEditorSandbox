import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from utils import loadStyleSheet
from PyQt5.QtWidgets import *
from examples.calculatorExample.calculatorWindow import Calculator



if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    calculatorWindow = Calculator()

    styleSheetPath = os.path.join(os.path.join(os.path.dirname(__file__), "..", ".."), "qss/nodestyle.qss")
    loadStyleSheet(styleSheetPath)

    sys.exit(app.exec_())