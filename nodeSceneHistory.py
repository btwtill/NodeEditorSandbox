from errno import EBUSY

from nodeGraphicsEdge import QDMGraphicsEdge
from utils import dumpException

DEBUG = False

class SceneHistory():
    def __init__(self, scene):
        self.scene = scene

        self.clear()
        self.historyLimit = 32

        self.undoSelectionHasChanged = False

        self._historyModifiedListeners = []
        self._historyStoredListeners = []
        self._historyRestoredListeners = []

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

    def addHistoryStoredListener(self, callback):
        self._historyStoredListeners.append(callback)

    def addHistoryRestoreListener(self, callback):
        self._historyRestoredListeners.append(callback)

    def restoreHistory(self):

        if DEBUG : print("HISTORY : DEBUG : Restoring History .... currentStep: @%d: " %
                         self.historyCurrentStep, "(%d)" % len(self.historyStack))
        self.restoreHistoryStamp(self.historyStack[self.historyCurrentStep])

        for callback in self._historyModifiedListeners: callback()
        for callback in self._historyRestoredListeners: callback()

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
        for callback in self._historyStoredListeners: callback()

    def createHistoryStamp(self, desc):

        if DEBUG : print("HISTORY : DEBUG : Current Selected history Stamp Items", self.scene.grScene.selectedItems())

        historyStamp = {
            'desc' : desc,
            'snapshot' : self.scene.serialize(),
            'selection' : self.captureCurrentSelection(),
        }

        return historyStamp

    def captureCurrentSelection(self):
        selectedObjects = {
            'nodes': [],
            'edges': [],
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'): selectedObjects['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'): selectedObjects['edges'].append(item.edge.id)
        return selectedObjects

    def restoreHistoryStamp(self, historyStamp):


        try:
            self.undoSelectionHasChanged = False
            previouseSelection = self.captureCurrentSelection()
            if DEBUG : print("SCENEHISTORY:: --restoehistoryStamp:: Selected Nodes Before Restoring Stamp ",
                             previouseSelection['nodes'])
            self.scene.deserialize(historyStamp['snapshot'])

            for edge in self.scene.edges: edge.grEdge.setSelected(False)

            for edgeId in historyStamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edgeId:
                        edge.grEdge.setSelected(True)
                        break

            for node in self.scene.nodes: node.grNode.setSelected(False)

            for nodeId in historyStamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == nodeId:
                        node.grNode.setSelected(True)
                        break

            currentSelection = self.captureCurrentSelection()
            if DEBUG : print("SCENEHISTORY:: --restorehistoryStamp:: Selected Nodes After Restoring Stamp ",
                             currentSelection['nodes'])

            self.scene._lastSelectedItems = self.scene.getSelectedItems()

            if (currentSelection['nodes'] != previouseSelection['nodes'] or
                currentSelection['edges'] != previouseSelection['edges']):
                if DEBUG : print("SCENEHISTORY:: --restoehistoryStamp:: Selection has Changed")
                self.undoSelectionHasChanged = True

        except Exception as e: dumpException(e)

        if DEBUG : print("HISTORY : DEBUG : Restore : ", historyStamp)