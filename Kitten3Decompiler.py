from BlockShadowCreator import SHADOW_ALL_TYPES
import xml.etree.ElementTree as ET
import json


# 基础反编译器类
class BlockDecompiler:
    def __init__(self, compiled_block: dict):
        self.compiled_block = compiled_block
        self.type = compiled_block.get("type", "unknown_type")
        self.id = compiled_block.get("id", "unknown_id")
        self.params = compiled_block.get("params", {})
        self.child_block = compiled_block.get("child_block", [])
        self.conditions = compiled_block.get("conditions", [])
        self.next_block = compiled_block.get("next_block", {})

    def create_field(self, name, value) -> ET.Element:
        """生成 field 元素"""
        field = ET.Element("field", {"name": name})
        field.text = str(value)
        return field

    def toxml(self):
        """将块转换为 XML"""
        label = self.get_block_label()
        block = ET.Element(
            label, {"type": self.type, "id": self.id, "visible": "visible"}
        )

        # 处理 params
        self.parms(block)

        # 处理子块
        self.children(block)

        # 处理下一个块
        self.nexts(block)

        return block

    def get_block_label(self):
        if self.type == "logic_empty":
            return "empty"
        elif self.type in SHADOW_ALL_TYPES:
            return "shadow"
        else:
            return "block"

    def nexts(self, block):
        if self.next_block:
            next_element = ET.SubElement(block, "next")
            next_element.append(getBlockDecompiler(self.next_block).toxml())

    def children(self, block):
        if isinstance(self.child_block, list) and self.child_block:
            if len(self.child_block) == 1:
                if self.child_block[0]:
                    statement = ET.SubElement(block, "statement", {"name": "DO"})
                    statement.append(getBlockDecompiler(self.child_block[0]).toxml())
            else:
                statement_id = 0
                for child in self.child_block:
                    if child:
                        statement = ET.SubElement(
                            block, "statement", {"name": f"DO{statement_id}"}
                        )
                        statement.append(getBlockDecompiler(child).toxml())
                        statement_id += 1

    def parms(self, block):
        for key, value in self.params.items():
            if isinstance(value, str):
                block.append(self.create_field(key, value))
            elif isinstance(value, dict):
                value_element = ET.SubElement(block, "value", {"name": key})
                value_block = getBlockDecompiler(value)
                if value_block.get_block_label() == "block":
                    # value_element.append()
                    # 这里应该生成一个shadow或 empty 块
                    pass
                value_element.append(value_block.toxml())

    def __str__(self):
        return ET.tostring(self.toxml(), encoding="unicode")


# 特殊积木反编译器：ControlsIfDecompiler
class ControlsIfDecompiler(BlockDecompiler):
    def children(self, block):
        statement_id = 0
        for child in self.child_block:
            if statement_id + 1 == len(self.child_block):
                statement_name = "ELSE"
            else:
                statement_name = f"DO{statement_id}"
            if child:
                statement = ET.SubElement(block, "statement", {"name": statement_name})
                statement.append(getBlockDecompiler(child).toxml())
                statement_id += 1

    def decompile_conditions(self, block):
        condition_id = 0
        for child in self.conditions:
            condition = ET.SubElement(block, "value", {"name": f"IF{condition_id}"})
            value_block = getBlockDecompiler(child)
            condition.append(value_block.toxml())
            if value_block.get_block_label() == "block":
                condition.append(
                    ET.fromstring(
                        '<empty type= "logic_empty" editable= "false" visible= \"visible\"><field name= "BOOL"></field></empty>'
                    )
                )
            condition_id += 1

    def toxml(self):
        label = self.get_block_label()
        block = ET.Element(
            label, {"type": self.type, "id": self.id, "visible": "visible"}
        )
        else_if_num = len(self.conditions) - 1
        if else_if_num == 0:
            mutation_parameters = {"else": "1"}
        else:
            mutation_parameters = {"elseif": str(else_if_num), "else": "1"}
        self.mutation = ET.SubElement(
            block, "mutation", mutation_parameters
        )
        # 处理 params
        self.parms(block)
        # 处理子块
        self.children(block)
        # 处理下一个块
        self.nexts(block)
        self.decompile_conditions(block)
        return block


class ControlsIfNoElseDecompiler(ControlsIfDecompiler):
    def children(self, block):
        statement_id = 0
        for child in self.child_block:
            if child != None:
                statement_name = f"DO{statement_id}"
                statement = ET.SubElement(block, "statement", {"name": statement_name})
                statement.append(getBlockDecompiler(child).toxml())
                statement_id += 1
            else:
                pass

    def toxml(self):
        block = super().toxml()
        block.remove(self.mutation)
        return block


# 特殊积木反编译器：TextJoinDecompiler
class TextJoinDecompiler(BlockDecompiler):
    def toxml(self):
        block = super().toxml()
        mutation = ET.SubElement(block, "mutation", {"items": str(len(self.params))})
        return block


class Procedures2DefDecompiler(BlockDecompiler):
    """定义函数的积木的反编译"""

    def __init__(self, compiled_block):
        super().__init__(compiled_block)
        self.procedure_name = compiled_block.get("procedure_name", "")

    def parms(self, block):
        # return super().parms(block)
        mutation = ET.SubElement(block, "mutation")
        parm_id = 0
        for key, value in self.params.items():
            arg_element = ET.SubElement(mutation, "arg", {"name": key})
            arg_element.text = ""
            value_element = ET.SubElement(block, "value", {"name": f"PARAMS{parm_id}"})
            value_element.append(
                ET.fromstring(
                    '<shadow type= "math_number"><field constraints= "-Infinity,Infinity,0," name= "NUM"></field></shadow>'
                )
            )
            value_element.append(
                ET.fromstring(
                    f'<block type= "procedures_2_stable_parameter" inline= "{value}"><field name= "param_name">{key}</field></block>'
                )
            )
            parm_id += 1
        pass

    def children(self, block):
        statement = ET.SubElement(block, "statement", {"name": "STACK"})
        statement.append(getBlockDecompiler(self.child_block[0]).toxml())

    def toxml(self):
        block = super().toxml()
        block.append(self.create_field("NAME", self.procedure_name))
        return block


class Procedures2CallNoReturnDecompiler(BlockDecompiler):
    """没有返回值函数的调用积木的反编译器"""

    def __init__(self, compiled_block):
        super().__init__(compiled_block)
        self.procedure_name = compiled_block.get("procedure_name", "")

    def parms(self, block):
        mutation = ET.SubElement(block, "mutation", {"name": self.procedure_name})
        arg_id = 0
        for key, value in self.params.items():
            if isinstance(value, str):
                block.append(self.create_field(key, value))
            elif isinstance(value, dict):
                value_element = ET.SubElement(block, "value", {"name": f"ARG{arg_id}"})
                value_element.append(getBlockDecompiler(value).toxml())
            parameter_shadow_element = ET.Element(
                "procedures_2_parameter_shadow", {"name": key}
            )
            parameter_shadow_element.text = ""
            mutation.append(parameter_shadow_element)
            arg_id += 1

    def toxml(self):
        block = super().toxml()
        block.append(self.create_field("NAME", self.procedure_name))
        return block


class Procedures2CallReturnDecompiler(Procedures2CallNoReturnDecompiler):
    """有返回值函数的调用积木的反编译器"""

    pass


# 特殊积木映射表
SPECIAL_DECOMPILER_MAP = {
    "controls_if": ControlsIfDecompiler,
    "controls_if_no_else": ControlsIfNoElseDecompiler,
    "text_join": TextJoinDecompiler,
    "procedures_2_defnoreturn": Procedures2DefDecompiler,
    "procedures_2_callnoreturn": Procedures2CallNoReturnDecompiler,
    "procedures_2_callreturn": Procedures2CallReturnDecompiler,
}


# 根据积木类型获取对应的反编译器
def getBlockDecompiler(compiled_block: dict) -> BlockDecompiler:
    block_type = compiled_block.get("type", "unknown_type")
    decompiler_class = SPECIAL_DECOMPILER_MAP.get(block_type, BlockDecompiler)
    return decompiler_class(compiled_block)


class ActorDecompiler:
    """对角色反编译"""

    def __init__(self, work, actor: dict, compiledBlocks: dict) -> None:
        self.work = work
        self.actor: dict = actor
        self.compiled = compiledBlocks
        self.blocks = {}
        self.connections = {}

    def prepare(self):
        # 准备角色的积木数据
        self.onPrepare()
        # self.blocks["blocksXML"] = ""

        # # 将积木数据与角色关联
        # self.actor["block_data_json"] = {
        #     "blocks": self.blocks,
        #     "connections": self.connections,
        #     "comments": {}
        # }

    def start(self):
        # 开始反编译角色
        self.onStart()
        blocksXML = "<variables></variables>"
        # 反编译角色的其余积木
        for id, compiledBlock in self.compiled["compiled_block_map"].items():
            self.blocks[id] = self.decompileBlock(compiledBlock)
            blocksXML += self.blocks[id]

        # 反编译角色的所有函数
        for name, compiledFunction in self.compiled["procedures"].items():
            self.onStartFunction(name)
            self.blocks[name] = self.decompileFunction(compiledFunction)
            blocksXML += self.blocks[name]

        self.actor["blocksXML"] = blocksXML

    def decompileFunction(self, compiledFunction: dict) -> str:
        # 反编译函数，返回字符串
        self.onPrepareFunction(compiledFunction["id"])
        decompiler = getBlockDecompiler(compiledFunction)
        return ET.tostring(decompiler.toxml(), encoding="unicode")

    def decompileBlock(self, compiledBlock: dict) -> str:
        # 反编译单个积木，返回字符串
        decompiler = getBlockDecompiler(compiledBlock)
        return ET.tostring(decompiler.toxml(), encoding="unicode")

    # 钩子方法，提供扩展点
    def onPrepare(self):
        pass

    def onPrepareFunction(self, name):
        pass

    def onStart(self):
        pass

    def onStartFunction(self, name):
        pass


class Kitten3WorkDecompiler:

    def __init__(self, workInfo: dict, compiledWork: dict) -> None:
        self.workInfo: dict = workInfo
        self.work: dict = compiledWork

    def start(self):
        # 开始反编译流程
        self.onStart()

        # 创建角色反编译器
        decompilers = []
        for actorCompiledBlocks in self.work["compile_result"]:
            actor = ActorDecompiler(
                self, self.getActor(actorCompiledBlocks["id"]), actorCompiledBlocks
            )
            self.onCreateActor(actor)
            decompilers.append(actor)

        # 准备所有角色
        self.onPrepareActors()
        for decompiler in decompilers:
            decompiler.prepare()

        # 开始反编译所有角色
        self.onStartActors()
        for decompiler in decompilers:
            decompiler.start()

        # 写入作品信息
        self.writeWorkInfo()

        # 清理不必要的数据
        self.clean()

        # 完成反编译
        self.onFinish()
        return self.work

    def getActor(self, actorID: str) -> dict:
        # 获取角色或场景信息
        theatre: dict = self.work["theatre"]
        try:
            return theatre["actors"][actorID]
        except KeyError:
            return theatre["scenes"][actorID]

    def clean(self):
        # 清理不必要的字段
        self.onClean()
        for key in {"compile_result", "preview", "author_nickname"}:
            self.work.pop(key, None)

    def writeWorkInfo(self):
        # 写入作品信息
        self.onWriteWorkInfo()
        self.work["hidden_toolbox"] = {"toolbox": [], "blocks": []}
        self.work["work_source_label"] = 0
        self.work["sample_id"] = ""
        self.work["project_name"] = self.workInfo["name"]
        self.work["toolbox_order"] = self.work["last_toolbox_order"] = [
            "hardware_ideali",
            "hardware_ideali_asr",
            "hardware_ideali_smartcar",
            "hardware_grovezero",
            "event",
            "control",
            "action",
            "appearance",
            "audio",
            "pen",
            "sensing",
            "operator",
            "data",
            "procedure",
            "physic",
            "ai",
            "cloud_variable",
            "advanced",
            "hardware_arduino",
            "hardware_weeemake",
            "hardware_microbit",
            "camera",
            "video",
            "wood",
            "cognitive",
            "ai_lab",
        ]

    # 可扩展的钩子方法
    def onStart(self):
        pass

    def onCreateActor(self, actor):
        pass

    def onPrepareActors(self):
        pass

    def onStartActors(self):
        pass

    def onWriteWorkInfo(self):
        pass

    def onClean(self):
        pass

    def onFinish(self):
        pass
