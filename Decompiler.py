from BlockShadowCreator import *

class WorkDecompiler:
    
    def __init__(self, workInfo, compiledWork) -> None:
        self.workInfo = workInfo
        self.work = compiledWork
        self.functions = {}
    
    def start(self):
        self.onStart()
        decompilers = []
        for ActorcompiledBlocks in self.work["compile_result"]:
            actor = ActorDecompiler(self, self.getActor(ActorcompiledBlocks["id"]), ActorcompiledBlocks)
            self.onCreateActor(actor)
            decompilers.append(actor)
        self.onPrepareActors()
        for decompiler in decompilers:
            decompiler.prepare()
        self.onStartActors()
        for decompiler in decompilers:
            decompiler.start()
        self.writteWorkInfo()
        self.clean()
        self.onFinish()
        return self.work

    def getActor(self, actorID):
        theatre = self.work["theatre"]
        try:
            return theatre["actors"][actorID]
        except KeyError:
            return theatre["scenes"][actorID]

    def clean(self):
        self.onClean()
        for key in { "compile_result", "preview", "author_nickname" }:
            try:
                del self.work[key]
            except KeyError:
                pass

    def writteWorkInfo(self):
        self.onWritteWorkInfo()
        self.work["hidden_toolbox"] = {
            "toolbox": [],
            "blocks": []
        }
        self.work["work_source_label"] = 0
        self.work["sample_id"] = ""
        self.work["project_name"] = self.workInfo["name"]
        self.work["toolbox_order"] = self.work["last_toolbox_order"] = [
            "event", "control", "action", "appearance", "audio", "pen", "sensing",
            "operator", "data", "data", "procedure", "mobile_control", "physic",
            "physics2", "cloud_variable", "cloud_list", "advanced", "ai_lab",
            "ai_game", "cognitive", "camera", "video", "wood", "arduino", "weeemake",
            "microbit", "ai", "midimusic"
        ]

    def onStart(self):
        print(f"开始反编译，作品名称：\033[4;32m{self.workInfo['name']}\033[0m。")

    def onCreateActor(self, actor): pass
    def onPrepareActors(self): pass
    def onStartActors(self): pass
    def onWritteWorkInfo(self): pass
    def onClean(self): pass
    def onFinish(self): pass
    
class ActorDecompiler:
    
    def __init__(self, work, actor, compiledBlocks) -> None:
        self.work = work
        self.actor = actor
        self.compiled = compiledBlocks
        self.blocks = {}
        self.connections = {}
        
    def prepare(self):
        self.onPrepare()
        self.actor["block_data_json"] = {
            "blocks": self.blocks,
            "connections": self.connections,
            "comments": {}
        }
        for name, compiledFunction in self.compiled["procedures"].items():
            self.onPrepareFunction(name)
            self.work.functions[name] = compiledFunction

    def start(self):
        self.onStart()
        for name, compiledFunction in self.compiled["procedures"].items():
            self.onStartFunction(name)
            self.work.functions[name] = Procedures2DefnoreturnDecompiler(compiledFunction, self).start()
        for id, compiledBlocks in self.compiled["compiled_block_map"].items():
            getBlockDecompiler(compiledBlocks, self).start()

    def onPrepare(self): pass
    def onPrepareFunction(self, name): pass
    def onStart(self): pass
    def onStartFunction(self, name): pass

def getBlockDecompiler(compiled, actor):
    type = compiled["type"]
    if type in SPECIAL_DECOMPILER_MAP:
        return SPECIAL_DECOMPILER_MAP[type](compiled, actor)
    return BlockDecompiler(compiled, actor)

class BlockDecompiler:

    def __init__(self, compiled, actor) -> None:
        self.compiled = compiled
        self.actor = actor
        self.block = {}
        self.connection = {}
        self.shadows = {}
        self.fields = {}

    def start(self):
        self.info()
        self.nexts()
        self.children()
        self.conditions()
        self.params()
        return self.block

    def info(self):
        self.id = self.block["id"] = self.compiled["id"]
        self.kind = self.compiled["kind"]
        self.type = self.block["type"] = self.compiled["type"]
        self.block["location"] = [0, 0]
        self.block["is_shadow"] = self.type in SHADOW_ALL_TYPES
        self.block["collapsed"] = False
        self.block["disabled"] = False
        self.block["deletable"] = True
        self.block["movable"] = True
        self.block["editable"] = True
        self.block["visible"] = "visible"
        self.block["shadows"] = self.shadows
        self.block["fields"] = self.fields
        self.block["field_constraints"] = {}
        self.block["field_extra_attr"] = {}
        self.block["comment"] = None
        self.block["mutation"] = ""
        self.block["is_output"] = self.type in SHADOW_ALL_TYPES or self.type in { "logic_boolean", "procedures_2_stable_parameter" }
        self.block["parent_id"] = None

        self.actor.connections[self.id] = self.connection
        self.actor.blocks[self.id] = self.block

    def nexts(self):
        if "next_block" in self.compiled:
            nextBlock = getBlockDecompiler(self.compiled["next_block"], self.actor).start()
            nextBlock["parent_id"] = self.id
            self.connection[nextBlock["id"]] = {
                "type": "next"
            }

    def children(self):
        if "child_block" in self.compiled:
            ChildBlocks = self.compiled["child_block"]
            for i in range(len(ChildBlocks)):
                if ChildBlocks[i] is not None:
                    childBlock = getBlockDecompiler(ChildBlocks[i], self.actor).start()
                    childBlock["parent_id"] = self.id
                    inputName = self.getChildInputName(i)
                    self.connection[childBlock["id"]] = {
                        "type": "input",
                        "input_type": "statement",
                        "input_name": inputName
                    }
                    self.shadows[inputName] = ""

    def getChildInputName(self, count): return "DO"

    def conditions(self):
        if "conditions" in self.compiled:
            conditions = self.compiled["conditions"]
            for i in range(len(conditions)):
                conditionBlock = getBlockDecompiler(conditions[i], self.actor).start()
                conditionBlock["parent_id"] = self.id
                inputName = f"IF{i}"
                if conditionBlock["type"] != "logic_empty":
                    self.connection[conditionBlock["id"]] = {
                        "type": "input",
                        "input_type": "value",
                        "input_name": inputName
                    }
                self.shadows[inputName] = createShadow("logic_empty", conditionBlock["id"])

    def params(self):
        for name, value in self.compiled["params"].items():
            if isinstance(value, dict):
                paramBlock = getBlockDecompiler(value, self.actor).start()
                paramBlock["parent_id"] = self.id
                paramType = paramBlock["type"]
                paramFields = paramBlock["fields"]
                if paramType in SHADOW_ALL_TYPES:
                    for inName, value in paramFields.items():
                        self.shadows[name] = createShadow(paramType, paramBlock["id"], value)
                else:
                    if name in { "condition", "BOOL" }:
                        shadowType = "logic_empty"
                    else:
                        shadowType = "math_number"
                    self.shadows[name] = createShadow(shadowType)
                self.connection[paramBlock["id"]] = {
                    "type": "input",
                    "input_type": "value",
                    "input_name": name
                }
            else:
                self.fields[name] = value

class ControlsIfDecompiler(BlockDecompiler):

    def start(self):
        block = super().start()
        childBlocks = self.compiled["child_block"]
        if len(childBlocks) == 2 and childBlocks[-1] is None:
            self.shadows["EXTRA_ADD_ELSE"] = ""
        else:
            self.block["mutation"] = f"<mutation elseif=\"{len(self.compiled['conditions']) - 1}\" else=\"1\"></mutation>"
            self.shadows["ELSE_TEXT"] = ""
        return block

    def getChildInputName(self, count):
        if count < len(self.compiled["conditions"]):
            return "DO" + str(count)
        else:
            return "ELSE"

class AskAndChooseDecompiler(BlockDecompiler):
    def start(self):
        block = super().start()
        self.block["mutation"] = f"<mutation items=\"{len(self.compiled['params']) - 1}\"></mutation>"
        return block

class TextJoinDecompiler(BlockDecompiler):
    def start(self):
        block = super().start()
        self.block["mutation"] = f"<mutation items=\"{len(self.compiled['params'])}\"></mutation>"
        return block

class TextSelectChangeableDecompiler(BlockDecompiler):
    def start(self):
        block = super().start()
        self.block["mutation"] = f"<mutation items=\"{len(self.compiled['params']) - 1}\"></mutation>"
        return block

class Procedures2DefnoreturnDecompiler(BlockDecompiler):

    def start(self):
        self.info()
        self.children()

        self.shadows["PROCEDURES_2_DEFNORETURN_DEFINE"] = ""
        self.shadows["PROCEDURES_2_DEFNORETURN_MUTATOR"] = ""
        self.fields["NAME"] = self.compiled["procedure_name"]
        mutation = ElementTree.Element("mutation")

        count = 0
        for name, value in self.compiled["params"].items():
            inputName = f"PARAMS{count}"
            
            arg = ElementTree.SubElement(mutation, "arg")
            arg.set("name", inputName)
            
            self.shadows[inputName] = createShadow("math_number")
            paramBlock = getBlockDecompiler({
                "id": randomBlockID(),
                "kind": "domain_block",
                "type": "procedures_2_stable_parameter",
                "params": {
                    "param_name": name,
                    "param_default_value": ""
                }
            }, self.actor).start()
            paramBlock["parent_id"] = self.block["id"]
            self.connection[paramBlock["id"]] = {
                "type": "input",
                "input_type": "value",
                "input_name": inputName
            }
            count += 1

        self.block["mutation"] = ElementTree.tostring(mutation, encoding='unicode')

        return self.block

    def getChildInputName(self, count): return "STACK"

class Procedures2ReturnValueDecompiler(BlockDecompiler):
    def start(self):
        block = super().start()
        self.shadows["PROCEDURES_2_DEFRETURN_RETURN"] = ""
        self.shadows["PROCEDURES_2_DEFRETURN_RETURN_MUTATOR"] = ""
        self.block["mutation"] = f"<mutation items=\"{len(self.compiled['params'])}\"></mutation>"
        return block

class Procedures2CallDecompiler(BlockDecompiler):

    def start(self):
        self.info()
        self.nexts()

        name = self.compiled["procedure_name"]
        try:
            functionID = self.actor.work.functions[name]["id"]
        except KeyError:
            functionID = randomBlockID()
            self.block["disabled"] = True
        self.shadows["NAME"] = ""
        self.fields["NAME"] = name
        mutation = ElementTree.Element("mutation")
        mutation.set("name", name)
        mutation.set("def_id", functionID)

        count = 0
        for name, value in self.compiled["params"].items():
            paramBlock = getBlockDecompiler(value, self.actor).start()
            self.shadows[f"ARG{count}"] = createShadow("default_value", paramBlock["id"])

            param = ElementTree.SubElement(mutation, "procedures_2_parameter_shadow")
            param.set("name", name)
            param.set("value", "0")

            self.connection[paramBlock["id"]] = {
                "type": "input",
                "input_type": "value",
                "input_name": f"ARG{count}"
            }

            count += 1

        self.block["mutation"] = ElementTree.tostring(mutation, encoding='unicode')

        return self.block

SPECIAL_DECOMPILER_MAP = {
    "controls_if": ControlsIfDecompiler,
    "ask_and_choose": AskAndChooseDecompiler,
    "text_join": TextJoinDecompiler,
    "text_select_changeable": TextSelectChangeableDecompiler,
    "procedures_2_defnoreturn": Procedures2DefnoreturnDecompiler,
    "procedures_2_return_value": Procedures2ReturnValueDecompiler,
    "procedures_2_callnoreturn": Procedures2CallDecompiler,
    "procedures_2_callreturn": Procedures2CallDecompiler
}
