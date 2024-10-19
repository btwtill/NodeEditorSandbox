import json
import os.path
from textwrap import indent

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication
from setuptools.command.editable_wheel import editable_wheel

from nodeEditorWidget import NodeEditorWidget

DEBUG = True

class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.filename = None

    def createAction(self, name, shortcut, tooltip, callback):

        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)

        return action

    def initUI(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.createAction('&New',
                                             'Ctrl+N', 'Create New Graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('&Open',
                                             'Ctrl+O', 'Open File', self.onFileOpen))
        fileMenu.addAction(self.createAction('&Save',
                                             'Ctrl+S', 'Save File', self.onFileSave))
        fileMenu.addAction(self.createAction('Save &As..',
                                             'Ctrl+Shift+S', 'Save File As', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('E&xit',
                                             'Ctrl+Q', 'Exit Application', self.close))

        editMenu = menuBar.addMenu('&Edit')

        editMenu.addAction(self.createAction('&Undo',
                                             'Ctrl+Z', 'Undo last Operation', self.onEditUndo))
        editMenu.addAction(self.createAction('&Redo',
                                             'Ctrl+Alt+Z', 'Redo last Operation', self.onEditRedo))

        fileMenu.addSeparator()
        editMenu.addAction(self.createAction('Cu&t',
                                             'Ctrl+X', 'Cut Selected Items', self.onEditCut))

        editMenu.addAction(self.createAction('&Copy',
                                             'Ctrl+C', 'Copy Selected Items to clipboard', self.onEditCopy))

        editMenu.addAction(self.createAction('&Paste',
                                             'Ctrl+V', 'Paste items from Clipboard', self.onEditPaste))

        fileMenu.addSeparator()

        editMenu.addAction(self.createAction('&Delete',
                                             'Del',
                                             'Delete Currently Selected Items',
                                             self.onEditDelete))

        nodeEditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeEditor)

        self.statusBar().showMessage('')
        self.statusMousePosition = QLabel('')
        self.statusBar().addPermanentWidget(self.statusMousePosition)
        nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)


        #set inital Window size
        self.setGeometry(200, 200, 800, 600)

        #set widget window title
        self.setWindowTitle('MNRB')

        # display
        self.show()

    def onScenePosChanged(self, x, y):
        self.statusMousePosition.setText("Scene Pos: [%d, %d]" % (x, y))

    def onFileNew(self):
        if DEBUG : print("Window : DEBUG : On File new!")
        self.centralWidget().scene.clearScene()

    def onFileOpen(self):
        if DEBUG : print("Window : DEBUG : Open")
        fname, filter = QFileDialog.getOpenFileName(self, ' Open graph from file')
        if fname == '':
            return
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)

    def onFileSave(self):
        if DEBUG : print("Window : DEBUG : Save")
        if self.filename == None: return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("Successfully saved %s" % self.filename)

    def onFileSaveAs(self):
        if DEBUG : print("Window : DEBUG : Save As")

        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to File')

        if fname == '':
            return
        self.filename = fname
        self.onFileSave()

    def onEditUndo(self):
        if DEBUG : print("Window : DEBUG : On Edit Undo")
        self.centralWidget().scene.sceneHistory.undo()

    def onEditRedo(self):
        self.centralWidget().scene.sceneHistory.redo()
        if DEBUG : print("Window : DEBUG : On Edit Redo")


    def onEditDelete(self):
        if DEBUG : print("Window : DEBUG : On Edit Delete")
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete = True)
        strData = json.dumps(data, indent = 4)
        QApplication.instance().clipboard().setText(strData)

    def onEditCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)#

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

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)
