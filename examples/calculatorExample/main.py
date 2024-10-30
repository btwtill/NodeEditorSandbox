import sys
from PyQt5.QtWidgets import *
from examples.calculatorExample.calculatorWindow import Calculator

if __name__ == "__main__":


    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    calculatorWindow = Calculator()

    sys.exit(app.exec_())