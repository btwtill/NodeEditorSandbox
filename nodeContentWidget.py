from PyQt5.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QWidget


class QDMNodeContentWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):

        self.contentLayout = QVBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.contentLayout)

        self.contentLabel = QLabel("Title")
        self.contentLayout.addWidget(self.contentLabel)
        self.contentLayout.addWidget(QTextEdit("Content"))