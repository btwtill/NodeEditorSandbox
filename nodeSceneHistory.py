from errno import EBUSY

from nodeGraphicsEdge import QDMGraphicsEdge
from utils import dumpException

DEBUG = False

class SceneHistory():
    def __init__(self, scene):
        self.scene = scene

        self.clear()
        self.historyLimit = 32

        self._historyModifiedListeners = []

    def clear(self):
        self.historyStack = []
        self.historyCurrentStep = -1

    def storeInitialHistoryStamp(self):
        self.storeHistory("Inital History Stamp")

    def canUndo(self):
        return self.historyCurrentStep > 0

    def canRedo(self):
        return self.historyCurrentStep +1 < len(self.historyStack)

    def undo(self):
        if DEBUG : print("HISTORY : DEBUG : UNDO")

        if self.canUndo():
            self.historyCurrentStep -= 1
            self.restoreHistory()
            self.scene.hasBeenModified = True

    def redo(self):
        if DEBUG : print("HISTORY : DEBUG : REDO")

        if self.canRedo():
            self.historyCurrentStep += 1
            self.restoreHistory()
            self.scene.hasBeenModified = True

    def addHistoryModifiedListener(self, callback):
        self._historyModifiedListeners.append(callback)

    def restoreHistory(self):

        if DEBUG : print("HISTORY : DEBUG : Restoring History .... currentStep: @%d: " %
                         self.historyCurrentStep, "(%d)" % len(self.historyStack))
        self.restoreHistoryStamp(self.historyStack[self.historyCurrentStep])

        for callback in self._historyModifiedListeners: callback()

    def storeHistory(self, desc, setModified = False):

        if setModified:
            self.scene.hasBeenModified = True

        if DEBUG : print("HISTORY : DEBUG : Storing History" , '"%s"' % desc, ".... currentStep: @%d: " %
                         self.historyCurrentStep, "(%d)" % len(self.historyStack))

        if self.historyCurrentStep +1 < len(self.historyStack):
            self.historyStack = self.historyStack[0:self.historyCurrentStep+1]

        if self.historyCurrentStep +1 >= self.historyLimit:
            self.historyStack = self.historyStack[1:]
            self.historyCurrentStep -= 1

        hs = self.createHistoryStamp(desc)

        self.historyStack.append(hs)
        self.historyCurrentStep += 1

        if DEBUG : print("HISTORY : DEBUG : --seting step to : ", self.historyCurrentStep)

        for callback in self._historyModifiedListeners: callback()

    def createHistoryStamp(self, desc):

        if DEBUG : print("HISTORY : DEBUG : Current Selected history Stamp Items", self.scene.grScene.selectedItems())

        selectedObjects = {
            'nodes' : [],
            'edges' : [],
        }

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                selectedObjects['nodes'].append(item.node.id)
            elif isinstance(item, QDMGraphicsEdge):
                selectedObjects['edges'].append(item.edge.id)

        historyStamp = {
            'desc' : desc,
            'snapshot' : self.scene.serialize(),
            'selection' : selectedObjects,
        }

        return historyStamp

    def restoreHistoryStamp(self, historyStamp):

        self.scene.deserialize(historyStamp['snapshot'])
        try:
            for edgeId in historyStamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edgeId:
                        edge.grEdge.setSelected(True)
                        break

            for nodeId in historyStamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == nodeId:
                        node.grNode.setSelected(True)
                        break
        except Exception as e: dumpException(e)

        if DEBUG : print("HISTORY : DEBUG : Restore : ", historyStamp)