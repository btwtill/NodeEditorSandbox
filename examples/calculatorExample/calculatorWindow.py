import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from examples.calculatorExample.calculatorConf import CALC_NODES
from nodeEditorWindow import NodeEditorWindow
from utils import dumpException
from examples.calculatorExample.calculatorSubWindow import CalculatorSubWindow
from calculatorDragListBox import QDMDragListBox
from utils import pp

DEBUG = False

class Calculator(NodeEditorWindow):

    def initUI(self):

        self.nameCompany = "TLPF"
        self.nameProduct = "Calculator NodeEditor"

        self.emptyIcon = QIcon(".")

        if DEBUG:
            print("CALCULATORWINDOW:: -initUI:: Registred Nodes:")
            pp(CALC_NODES)

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

        self.createNodesDock()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Calc Example")

        self.show()

    def createNodesDock(self):
        self.nodesListWidget = QDMDragListBox()

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.nodesDock)

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actionAbout)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def createActions(self):
        super().createActions()

        self.actionClose = QAction("Cl&ose", self,
                                   statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actionCloseAll = QAction("Close &All", self,
                                   statusTip="Close all windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actionTile = QAction("&Tile", self,
                                  statusTip = "Tile the windows", triggered = self.mdiArea.tileSubWindows)
        self.actionCascade = QAction("&Cascade", self,
                                     statusTip = "Cascade the Windows", triggered = self.mdiArea.cascadeSubWindows)
        self.actionNext = QAction("Ne&xt", self,
                                  shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next Window",
                                  triggered=self.mdiArea.activateNextSubWindow)
        self.actionPreviouse = QAction("Pre&vious", self,
                                       shortcut=QKeySequence.PreviousChild,
                                       statusTip="Move the focus to the previouse Window",
                                       triggered=self.mdiArea.activatePreviousSubWindow)
        self.actionSeparator = QAction(self)
        self.actionSeparator.setSeparator(True)
        self.actionAbout = QAction("&About", self,
                                   statusTip="Shot the applications about box", triggered=self.about)

    def createToolBars(self):
        pass

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def updateMenus(self):
        activeMdiChild = self.getCurrentNodeEditorWidget()
        hasMdiChild = (activeMdiChild is not None)

        self.actionSave.setEnabled(hasMdiChild)
        self.actionSaveAs.setEnabled(hasMdiChild)
        self.actionClose.setEnabled(hasMdiChild)
        self.actionCloseAll.setEnabled(hasMdiChild)
        self.actionTile.setEnabled(hasMdiChild)
        self.actionCascade.setEnabled(hasMdiChild)
        self.actionNext.setEnabled(hasMdiChild)
        self.actionPreviouse.setEnabled(hasMdiChild)
        self.actionSeparator.setSeparator(hasMdiChild)

        self.updateEditMenu()

    def updateWindowMenu(self):

        self.windowMenu.clear()

        toolbarNodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbarNodes.setCheckable(True)
        toolbarNodes.triggered.connect(self.onWindowNodesToolbar)

        toolbarNodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actionClose)
        self.windowMenu.addAction(self.actionCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actionTile)
        self.windowMenu.addAction(self.actionCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actionNext)
        self.windowMenu.addAction(self.actionPreviouse)
        self.windowMenu.addAction(self.actionNext)
        self.windowMenu.addAction(self.actionSeparator)

        windows = self.mdiArea.subWindowList()
        self.actionSeparator.setVisible(len(windows) !=0 )

        for i, window in enumerate(windows):
            child = window.widget()
            text = "%d %s" % (i + 1, child.getUserFriendlyFileName())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def updateEditMenu(self):
        activeMdiChild = self.getCurrentNodeEditorWidget()
        hasMdiChild = (activeMdiChild is not None)

        self.actionPaste.setEnabled(hasMdiChild)
        self.actionCut.setEnabled(hasMdiChild and activeMdiChild.hasSelectedItems())
        self.actionCopy.setEnabled(hasMdiChild and activeMdiChild.hasSelectedItems())
        self.actionDelete.setEnabled(hasMdiChild and activeMdiChild.hasSelectedItems())

        self.actionUndo.setEnabled(hasMdiChild and activeMdiChild.canUndo())
        self.actionRedo.setEnabled(hasMdiChild and activeMdiChild.canRedo())

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def getCurrentNodeEditorWidget(self):
        # We are Returning nodeEditor Widget Here
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subWindow = self.createMdiChild()
            subWindow.show()
        except Exception as e: dumpException(e)

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, ' Open graph from file',
                                                      self.getFileDialogDirectory(), self.getFileDialogFilter())
        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        #create new Subwindow and open file
                        nodeEditor = CalculatorSubWindow()

                        if nodeEditor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            nodeEditor.setTitle()

                            subWindow = self.createMdiChild(nodeEditor)
                            subWindow.show()
                        else:
                            nodeEditor.close()
        except Exception as e: dumpException(e)

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def about(self):
        QMessageBox.about(self, "About Calculator Example",
                          "This is a test Example Calculator Project"
                          "demonstating the use of multiple windows in an application with the use of the Node Editor")

    def createMdiChild(self, childWidget=None):

        nodeEditor = childWidget if childWidget is not None else CalculatorSubWindow()
        subWindow = self.mdiArea.addSubWindow(nodeEditor)

        nodeEditor.scene.sceneHistory.addHistoryModifiedListener(self.updateEditMenu)

        nodeEditor.addCloseEventListener(self.onSubWindowClose)

        return subWindow

    def onSubWindowClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, fileName):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == fileName:
                return window
        return None

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

            #import sys
            #sys.exit(0)