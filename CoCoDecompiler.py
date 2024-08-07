class CoCoWorkDecompiler:

    def __init__(self, workInfo, compiledWork) -> None:
        self.workInfo = workInfo
        self.work = compiledWork

    def start(self):
        self.onStart()
        self.writeWorkInfo()
        self.clean()
        self.onFinish()
        return self.work

    def clean(self):
        self.onClean()
        for key in { "id", "screenList",
                    "widgetMap", "variableMap", "gridMap", "blockJsonMap",
                    "initialScreenId", "apiToken",
                    "imageFileMap", "soundFileMap", "iconFileMap", "fontFileMap",
                    "blockCode" }:
            try:
                del self.work[key]
            except KeyError:
                pass

    def writeWorkInfo(self):
        self.work["authorId"] = self.workInfo["author"]["ID"]
        self.work["title"] = self.workInfo["name"]
        self.work["screens"] = {}
        self.work["screenIds"] = []
        for screen in self.work["screenList"]:
            ID = screen["id"]
            screen["snapshot"] = ""
            self.work["screens"][ID] = screen
            self.work["screenIds"].append(ID)
            screen["primitiveVariables"] = []
            screen["arrayVariables"] = []
            screen["objectVariables"] = []
            screen["broadcasts"] = ["Hi"]
            screen["widgets"] = {}
            for widgetID in screen["widgetIds"] + screen["invisibleWidgetIds"]:
                screen["widgets"][widgetID] = self.work["widgetMap"][widgetID]
                del self.work["widgetMap"][widgetID]
        self.work["blockly"] = {}
        for screenID, blocks in self.work["blockJsonMap"].items():
            self.work["blockly"][screenID] = {
                "screenId": screenID,
                "workspaceJson": blocks,
                "workspaceOffset": { "x": 0, "y": 0 }
            }
        self.work["imageFileList"] = list(self.work["imageFileMap"].values())
        self.work["soundFileList"] = list(self.work["soundFileMap"].values())
        self.work["iconFileList"] = list(self.work["iconFileMap"].values())
        self.work["fontFileList"] = list(self.work["fontFileMap"].values())
        varCount = 0
        listCount = 0
        dictCount = 0
        self.work["globalVariableList"] = []
        self.work["globalArrayList"] = []
        self.work["globalObjectList"] = []
        for ID, value in self.work["variableMap"].items():
            if (isinstance(value, list)):
                listCount += 1
                self.work["globalArrayList"].append({
                    "id": ID,
                    "name": f"列表{listCount}",
                    "defaultValue": value,
                    "value": value
                })
            elif (isinstance(value, dict)):
                dictCount += 1
                self.work["globalObjectList"].append({
                    "id": ID,
                    "name": f"字典{dictCount}",
                    "defaultValue": value,
                    "value": value
                })
            else:
                varCount += 1
                self.work["globalVariableList"].append({
                    "id": ID,
                    "name": f"变量{varCount}",
                    "defaultValue": value,
                    "value": value
                })
        self.work["globalWidgets"] = self.work["widgetMap"]
        self.work["globalWidgetIds"] = list(self.work["widgetMap"].keys())
        self.work["sourceTag"] = 1
        self.work["sourceId"] = ""

    def onStart(self): pass
    def onCreateActor(self, actor): pass
    def onPrepareActors(self): pass
    def onStartActors(self): pass
    def onWritteWorkInfo(self): pass
    def onClean(self): pass
    def onFinish(self): pass
