from PyQt5.QtWidgets import QMainWindow

from nodeEditorWidget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('File')

        nodeEditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeEditor)

        #set inital Window size
        self.setGeometry(200, 200, 800, 600)

        #set widget window title
        self.setWindowTitle('MNRB')

        # display
        self.show()
