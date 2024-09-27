from PyQt5.QtWidgets import QMainWindow, QAction

from nodeEditorWidget import NodeEditorWidget

DEBUG = True

class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def createAction(self, name, shortcut, tooltip, callback):

        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)

        return action

    def initUI(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.createAction('&New', 'Ctrl+N', 'Create New Graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('&Open', 'Ctrl+O', 'Open File', self.onFileOpen))
        fileMenu.addAction(self.createAction('&Save', 'Ctrl+S', 'Save File', self.onFileSave))
        fileMenu.addAction(self.createAction('Save &As..', 'Ctrl+Shift+S', 'Save File As', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('E&xit', 'Ctrl+Q', 'Exit Application', self.close))

        nodeEditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeEditor)

        #set inital Window size
        self.setGeometry(200, 200, 800, 600)

        #set widget window title
        self.setWindowTitle('MNRB')

        # display
        self.show()

    def onFileNew(self):
        if DEBUG : print("Window : DEBUG : On File new!")

    def onFileOpen(self):
        if DEBUG : print("Window : DEBUG : Open")

    def onFileSave(self):
        if DEBUG : print("Window : DEBUG : Save")

    def onFileSaveAs(self):
        if DEBUG : print("Window : DEBUG : Save As")

