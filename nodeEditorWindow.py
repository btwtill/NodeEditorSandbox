import json
import os.path
from textwrap import indent

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox

from nodeEditorWidget import NodeEditorWidget

DEBUG = True

class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.nameCompany = "TLPF"
        self.nameProduct = "NodeEditor"

        self.initUI()

    def initUI(self):

        self.createActions()
        self.createMenus()

        self.nodeEditor = NodeEditorWidget(self)
        self.nodeEditor.scene.addHasBeenModifiedListener(self.setTitle)

        self.setCentralWidget(self.nodeEditor)
        self.createStatusBar()

        #set inital Window size
        self.setGeometry(200, 200, 800, 600)

        self.setTitle()

        # display
        self.show()

    def createStatusBar(self):

        self.statusBar().showMessage('')
        self.statusMousePosition = QLabel('')
        self.statusBar().addPermanentWidget(self.statusMousePosition)
        self.nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)

    def createActions(self):

        self.actionNew = QAction('&New', self, shortcut= 'Ctrl+N',
                                 statusTip='Create New Graph', triggered=self.onFileNew)
        self.actionOpen = QAction('&Open', self, shortcut= 'Ctrl+O',
                                  statusTip='Open File', triggered=self.onFileOpen)
        self.actionSave = QAction('&Save', self, shortcut= 'Ctrl+S',
                                  statusTip='Save File', triggered=self.onFileSave)
        self.actionSaveAs = QAction('Save &As..', self, shortcut= 'Ctrl+Shift+S',
                                    statusTip='Save File As', triggered=self.onFileSaveAs)
        self.actionExit = QAction('E&xit', self, shortcut='Ctrl+Q',
                                  statusTip='Exit Application', triggered=self.close)

        self.actionUndo = QAction('&Undo', self, shortcut= 'Ctrl+Z',
                                  statusTip='Undo last Operation', triggered=self.onEditUndo)
        self.actionRedo = QAction('&Redo', self, shortcut= 'Ctrl+Alt+Z',
                                  statusTip='Redo last Operation', triggered=self.onEditRedo)
        self.actionCut = QAction('Cu&t', self, shortcut= 'Ctrl+X',
                                 statusTip='Cut Selected Items', triggered=self.onEditCut)
        self.actionCopy = QAction('&Copy', self, shortcut= 'Ctrl+C',
                                  statusTip='Copy Selected Items to clipboard', triggered=self.onEditCopy)
        self.actionPaste = QAction('&Paste', self, shortcut= 'Ctrl+V',
                                   statusTip='Paste items from Clipboard', triggered=self.onEditPaste)
        self.actionDelete = QAction('&Delete', self, shortcut='Del',
                                    statusTip='Delete Currently Selected Items', triggered=self.onEditDelete)

    def createMenus(self):

        menuBar = self.menuBar()

        self.fileMenu = menuBar.addMenu('&File')
        self.fileMenu.addAction(self.actionNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionOpen)
        self.fileMenu.addAction(self.actionSave)
        self.fileMenu.addAction(self.actionSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionExit)

        self.editMenu = menuBar.addMenu('&Edit')
        self.editMenu.addAction(self.actionUndo)
        self.editMenu.addAction(self.actionRedo)
        self.fileMenu.addSeparator()
        self.editMenu.addAction(self.actionCut)
        self.editMenu.addAction(self.actionCopy)
        self.editMenu.addAction(self.actionPaste)
        self.fileMenu.addSeparator()
        self.editMenu.addAction(self.actionDelete)

    def setTitle(self):
        title = "MNRB - "

        title += self.getCurrentNodeEditorWidget().getUserFriendlyFileName()

        self.setWindowTitle(title)

    def onScenePosChanged(self, x, y):
        self.statusMousePosition.setText("Scene Pos: [%d, %d]" % (x, y))

    def onFileNew(self):
        if self.maybeSave():
            if DEBUG : print("Window : DEBUG : On File new!")
            self.getCurrentNodeEditorWidget().scene.clearScene()
            self.getCurrentNodeEditorWidget().filename = None
            self.setTitle()

    def onFileOpen(self):
        if self.maybeSave():
            if DEBUG : print("Window : DEBUG : Open")
            fname, filter = QFileDialog.getOpenFileName(self, ' Open graph from file')
            if fname == '':
                return
            if os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)

    def onFileSave(self):
        if DEBUG : print("Window : DEBUG : Save")
        if self.getCurrentNodeEditorWidget().filename is None: return self.onFileSaveAs()
        self.getCurrentNodeEditorWidget().fileSave()
        self.statusBar().showMessage("Successfully saved %s" % self.getCurrentNodeEditorWidget().filename)

        return True

    def onFileSaveAs(self):
        if DEBUG : print("Window : DEBUG : Save As")

        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to File')

        if fname == '':
            return False

        self.getCurrentNodeEditorWidget().fileSave(fname)
        self.statusBar().showMessage("Successfully saved as %s" % self.getCurrentNodeEditorWidget().filename)
        return True

    def onEditUndo(self):
        if DEBUG : print("Window : DEBUG : On Edit Undo")
        self.getCurrentNodeEditorWidget().scene.sceneHistory.undo()

    def onEditRedo(self):
        self.getCurrentNodeEditorWidget().scene.sceneHistory.redo()
        if DEBUG : print("Window : DEBUG : On Edit Redo")

    def onEditDelete(self):
        if DEBUG : print("Window : DEBUG : On Edit Delete")
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete = True)
        strData = json.dumps(data, indent = 4)
        QApplication.instance().clipboard().setText(strData)

    def onEditCopy(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)#

        if DEBUG : print("NodeEditorWindow : DEBUG : Serielized Data : ", data)

        strData = json.dumps(data, indent=4)

        QApplication.instance().clipboard().setText(strData)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting not valid json data!", e)
            return

        if 'nodes' not in data:
            print("JSON does not contain any nodes!")
            return

        self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.hasBeenModified

    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def maybeSave(self):
        if not self.isModified():
            return True

        result = QMessageBox.warning(self, "About to loose your work!", "The file has been modified.",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if result == QMessageBox.Save:
            return self.onFileSave()
        elif result == QMessageBox.Cancel:
            return False
        else: return True

    def readSettings(self):
        settings = QSettings(self.nameCompany, self.nameProduct)
        position = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(position)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.nameCompany, self.nameProduct)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())