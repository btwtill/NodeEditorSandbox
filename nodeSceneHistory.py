
DEBUG = True

class SceneHistory():
    def __init__(self, scene):
        self.scene = scene


        self.historyStack = []
        self.historyCurrentStep = -1
        self.historyLimit = 8

    def undo(self):
        if DEBUG : print("HISTORY : DEBUG : UNDO")

        if self.historyCurrentStep > 0:
            self.historyCurrentStep -= 1
            self.restoreHistory()

    def redo(self):
        if DEBUG : print("HISTORY : DEBUG : REDO")

        if self.historyCurrentStep +1 < len(self.historyStack):
            self.historyCurrentStep += 1

            self.restoreHistory()


    def restoreHistory(self):
        if DEBUG : print("HISTORY : DEBUG : Restoring History .... currentStep: @%d: " %
                         self.historyCurrentStep, "(%d)" % len(self.historyStack))
        self.restoreHistoryStamp(self.historyStack[self.historyCurrentStep])


    def storeHistory(self, desc):
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


    def createHistoryStamp(self, desc):
        return desc



    def restoreHistoryStamp(self, historyStamp):
        if DEBUG : print("HISTORY : DEBUG : Restore : ", historyStamp)