from BlockShadowCreator import *
from MetaData import PROJECT

def decompile(workInfo, compiledCode):
    print(f"开始反编译，作品名称：\033[4;32m{workInfo['name']}\033[0m。")
    functions = {}
    decompilers = [ActorDecompiler(getActor(i["id"], compiledCode), i, functions)
                   for i in compiledCode["compile_result"]]
    for decompiler in decompilers:
        decompiler.decompilePrepare()
    for decompiler in decompilers:
        decompiler.decompileFunctions()
    for decompiler in decompilers:
        decompiler.decompileCode()
    writteWorkInfo(workInfo, compiledCode)
    clean(compiledCode)
    print("反编译完成。")
    
def getActor(actorID, compiledCode):
    theatre = compiledCode["theatre"]
    try:
        return theatre["actors"][actorID]
    except KeyError:
        return theatre["scenes"][actorID]
    
class ActorDecompiler:
    
    def __init__(self, actor, compiled, functions) -> None:
        self.blocks = {}
        self.connections = {}
        self.actor = actor
        self.compiled = compiled
        self.functions = functions

    def decompilePrepare(self):
        blocks = self.blocks
        connections = self.connections
        actor = self.actor
        
        print(f"正在准备角色 \033[4;32m{actor['name']}\033[0m……")
        actor["block_data_json"] = {
            "blocks": blocks,
            "connections": connections,
            "comments": {}
        }
        
    def decompileFunctions(self):
        actor = self.actor
        compiled = self.compiled
        functions = self.functions
        
        print(f"正在反编译角色 \033[4;32m{actor['name']}\033[0m 中的函数……")
        for name, compiledBlock in compiled["procedures"].items():
            print(f"正在反编译函数 \033[4;32m{name}\033[0m ……")
            functions[name] = BlockDecompiler(compiledBlock, self).decompile()
            
    def decompileCode(self):
        actor = self.actor
        compiled = self.compiled
        
        print(f"正在反编译角色 \033[4;32m{actor['name']}\033[0m 的代码……")
        for id, compiledBlock in compiled["compiled_block_map"].items():
            BlockDecompiler(compiledBlock, self).decompile()

class BlockDecompiler:

    def __init__(self, compiled, actor) -> None:
        self.block = {}
        self.connection = {}
        self.shadows = {}
        self.fields = {}
        self.compiled = compiled
        self.actor = actor

    def decompile(self):
        block = self.block
        connection = self.connection
        shadows = self.shadows
        fields = self.fields
        compiled = self.compiled
        actor = self.actor
        
        id = block["id"] = compiled["id"]
        kind = compiled["kind"]
        type = block["type"] = compiled["type"]
        block["comment"] = None
        block["location"] = [0, 0]
        block["is_shadow"] = type in SHADOW_ALL_TYPES
        block["collapsed"] = False
        block["disabled"] = False
        block["deletable"] = True
        block["movable"] = True
        block["editable"] = True
        block["visible"] = "visible"
        block["shadows"] = shadows
        block["fields"] = fields
        block["field_constraints"] = {}
        block["field_extra_attr"] = {}
        block["comment"] = None
        block["mutation"] = ""
        block["is_output"] = type in SHADOW_ALL_TYPES or type in { "logic_boolean", "procedures_2_stable_parameter" }
        block["parent_id"] = None
        
        if type in DECOMPILE_SPECIAL_MAP:
            DECOMPILE_SPECIAL_MAP[type](self)

        if "next_block" in compiled:
            nextBlock = BlockDecompiler(compiled["next_block"], actor).decompile()
            nextBlock["parent_id"] = id
            connection[nextBlock["id"]] = {
                "type": "next"
            }

        if "child_block" in compiled:
            ChildBlocks = compiled["child_block"]
            for i in range(len(ChildBlocks)):
                if ChildBlocks[i] is not None:
                    childBlock = BlockDecompiler(ChildBlocks[i], actor).decompile()
                    childBlock["parent_id"] = id
                    if kind in { "event_block", "responder_block" } or kind.startswith("repeat"):
                        inputName = "DO"
                    else:
                        inputName = CHILD_BLOCK_INPUT_NAME_GETTER_MAP[compiled["type"]](compiled, i)
                    connection[childBlock["id"]] = {
                        "type": "input",
                        "input_type": "statement",
                        "input_name": inputName
                    }
                    shadows[inputName] = ""

        if "conditions" in compiled:
            conditions = compiled["conditions"]
            for i in range(len(conditions)):
                conditionBlock = BlockDecompiler(conditions[i], actor).decompile()
                conditionBlock["parent_id"] = id
                inputName = CONDITIONS_INPUT_NAME_GETTER_MAP[compiled["type"]](i)
                if conditionBlock["type"] != "logic_empty":
                    connection[conditionBlock["id"]] = {
                        "type": "input",
                        "input_type": "value",
                        "input_name": inputName
                    }
                shadows[inputName] = createShadow("logic_empty", conditionBlock["id"])
                
        if kind in { "domain_block", "event_block", "wait_until", "procedures_2_parameter" } or kind.startswith("repeat"):
            for name, value in compiled["params"].items():
                if isinstance(value, dict):
                    paramBlock = BlockDecompiler(value, actor).decompile()
                    paramBlock["parent_id"] = id
                    paramType = paramBlock["type"]
                    paramFields = paramBlock["fields"]
                    if paramType in SHADOW_ALL_TYPES:
                        for inName, value in paramFields.items():
                            shadows[name] = createShadow(paramType, paramBlock["id"], value)
                    else:
                        if name in { "condition", "BOOL" }:
                            shadowType = "logic_empty"
                        else:
                            shadowType = "math_number"
                        shadows[name] = createShadow(shadowType)
                    connection[paramBlock["id"]] = {
                        "type": "input",
                        "input_type": "value",
                        "input_name": name
                    }
                else:
                    fields[name] = value

        actor.connections[id] = connection
        actor.blocks[id] = block
        return block

def decompileTextJoin(decompiler):
    block = decompiler.block
    compiled = decompiler.compiled
    block["mutation"] = f"<mutation items=\"{len(compiled['params'])}\"></mutation>"

def decompileControlsIf(decompiler):
    block = decompiler.block
    shadows = decompiler.shadows
    compiled = decompiler.compiled
    if len(compiled["child_block"]) == len(compiled["conditions"]):
        block["mutation"] = f"<mutation elseif=\"{len(compiled['conditions']) - 1}\"></mutation>"
        shadows["EXTRA_ADD_ELSE"] = ""
    else:
        block["mutation"] = f"<mutation elseif=\"{len(compiled['conditions']) - 1}\" else=\"1\"></mutation>"
        shadows["ELSE_TEXT"] = ""

def decompileProcedures2Defnoreturn(decompiler):
    block = decompiler.block
    connection = decompiler.connection
    shadows = decompiler.shadows
    fields = decompiler.fields
    compiled = decompiler.compiled
    actor = decompiler.actor

    shadows["PROCEDURES_2_DEFNORETURN_DEFINE"] = ""
    shadows["PROCEDURES_2_DEFNORETURN_MUTATOR"] = ""
    fields["NAME"] = compiled["procedure_name"]
    mutation = ElementTree.Element("mutation")

    count = 0
    for name, value in compiled["params"].items():
        inputName = f"PARAMS{count}"
        
        arg = ElementTree.SubElement(mutation, "arg")
        arg.set("name", inputName)
        
        shadows[inputName] = createShadow("math_number")
        paramBlock = BlockDecompiler({
            "id": randomBlockID(),
            "kind": "domain_block",
            "type": "procedures_2_stable_parameter",
            "params": {
                "param_name": name,
                "param_default_value": ""
            }
        }, actor).decompile()
        paramBlock["parent_id"] = block["id"]
        connection[paramBlock["id"]] = {
            "type": "input",
            "input_type": "value",
            "input_name": inputName
        }
        count += 1
        
    block["mutation"] = ElementTree.tostring(mutation, encoding='unicode')

def decompileProcedures2Callnoreturn(decompiler):
    block = decompiler.block
    connection = decompiler.connection
    shadows = decompiler.shadows
    fields = decompiler.fields
    compiled = decompiler.compiled
    actor = decompiler.actor
    
    name = compiled["procedure_name"]
    function = actor.functions[name]
    shadows["NAME"] = ""
    fields["NAME"] = name
    mutation = ElementTree.Element("mutation")
    mutation.set("name", name)
    mutation.set("def_id", function['id'])
    
    count = 0
    for name, value in compiled["params"].items():
        paramBlock = BlockDecompiler(value, actor).decompile()
        shadows[f"ARG{count}"] = createShadow("default_value", paramBlock["id"])
        
        param = ElementTree.SubElement(mutation, "procedures_2_parameter_shadow")
        param.set("name", name)
        param.set("value", "0")
        
        connection[paramBlock["id"]] = {
            "type": "input",
            "input_type": "value",
            "input_name": f"ARG{count}"
        }
        
        count += 1
        
    block["mutation"] = ElementTree.tostring(mutation, encoding='unicode')

DECOMPILE_SPECIAL_MAP = {
    "text_join": decompileTextJoin,
    "controls_if": decompileControlsIf,
    "procedures_2_defnoreturn": decompileProcedures2Defnoreturn,
    "procedures_2_callnoreturn": decompileProcedures2Callnoreturn
}

def getControlsIfChildBlockInputName(compiledBlock, count):
    if count < len(compiledBlock["conditions"]):
        return "DO" + str(count)
    else:
        return "ELSE"

CHILD_BLOCK_INPUT_NAME_GETTER_MAP = {
    "controls_if": getControlsIfChildBlockInputName,
    "procedures_2_defnoreturn": lambda compiledBlock, count: "STACK",
    "warp": lambda compiledBlock, count: "DO"
}

CONDITIONS_INPUT_NAME_GETTER_MAP = {
    "controls_if": lambda count: "IF" + str(count)
}


def writteWorkInfo(workInfo, compiledCode):
    print("正在写入作品信息……")
    compiledCode["hidden_toolbox"] = {
        "toolbox": [],
        "blocks": []
    }
    compiledCode["work_source_label"] = 0
    compiledCode["sample_id"] = ""
    compiledCode["project_name"] = f"{workInfo['name']} - 反编译自 {PROJECT.NAME}"
    compiledCode["toolbox_order"] = compiledCode["last_toolbox_order"] = [
        "event", "control", "action", "appearance", "audio", "pen", "sensing",
        "operator", "data", "data", "procedure", "mobile_control", "physic",
        "physics2", "cloud_variable", "cloud_list", "advanced", "ai_lab",
        "ai_game", "cognitive", "camera", "video", "wood", "arduino", "weeemake",
        "microbit", "ai", "midimusic"
    ]

def clean(compiledCode):
    print("正在清理……")
    del compiledCode["compile_result"]
    del compiledCode["preview"]
    del compiledCode["author_nickname"]
