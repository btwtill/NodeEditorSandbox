from textwrap import shorten

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodeEditorWindow import NodeEditorWindow
from utils import dumpException


class Calculator(NodeEditorWindow):

    def initUI(self):

        self.nameCompany = "TLPF"
        self.nameProduct = "Calculator NodeEditor"

        self.mdiArea = QMdiArea()

        #set the scrollbar behaviour
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        #arrange all subWindows in a tab bar fashion
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)

        #configure tab freatures
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)

        #configure the Main windows central widget
        self.setCentralWidget(self.mdiArea)

        #connect a function to the signal that is triggered when a subWindow is focused (activated)
        self.mdiArea.subWindowActivated.connect(self.updateMenus)

        #
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        #docking
        self.createNodesDock()

        self.readSettings()

        self.setWindowTitle("Calc Example")

        self.show()


    def createNodesDock(self):
        self.listWidget = QListWidget()
        self.listWidget.addItem("Add")
        self.listWidget.addItem("sub")
        self.listWidget.addItem("multi")

        self.items = QDockWidget("Nodes")
        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.items)

    def updateMenus(self):
        pass

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAction)

    def updateWindowMenu(self):
        pass

    def createActions(self):
        super().createActions()

        self.closeAction = QAction("Cl&ose", self,
                                   statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)

        self.closeAllAction = QAction("Close &All", self,
                                   statusTip="Close all windows", triggered=self.mdiArea.closeActiveSubWindow)

        self.tileAction = QAction("&Tile", self,
                                  statusTip = "Tile the windows", triggered = self.mdiArea.tileSubWindows)

        self.cascadeAction = QAction("&Cascade", self,
                                     statusTip = "Cascade the Windows", triggered = self.mdiArea.cascadeSubWindows)

        self.nextAction = QAction("Ne&xt", self,
                                  shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next Window",
                                  triggered=self.mdiArea.activateNextSubWindow)

        self.previouseAction = QAction("Pre&vious", self,
                                       shortcut=QKeySequence.PreviousChild,
                                       statusTip="Move the focus to the previouse Window",
                                       triggered=self.mdiArea.activatePreviousSubWindow)

        self.separatorAction = QAction(self)
        self.separatorAction.setSeparator(True)

        self.aboutAction = QAction("&About", self,
                                   statusTip="Shot the applications about box", triggered=self.about)

    
    def createToolBars(self):
        pass

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def about(self):
        QMessageBox.about(self, "About Calculator Example",
                          "This is a test Example Calculator Project"
                          "demonstating the use of multiple windows in an application with the use of the Node Editor")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()