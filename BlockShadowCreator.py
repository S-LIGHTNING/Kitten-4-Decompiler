from xml.etree import ElementTree

from Tool import randomBlockID

# 这些类型的积木完全嵌入在父母积木中，不是独立的积木，可以被其它积木覆盖在上面
SHADOW_ALL_TYPES = {
    "math_number",
    "controller_shadow",
    "text",
    "logic_empty",
    "lists_get",
    "broadcast_input",
    "get_audios",
    "get_whole_audios",
    "get_current_costume",
    "default_value",
    "get_current_scene",
    "get_sensing_current_scene"
}

# 参数信息
SHADOW_FIELD_ATTRIBUTES_MAP = {
    "math_number": {
        "name": "NUM",
        "constraints": "-Infinity,Infinity,0,",
        "allow_text": "true"
    },
    "controller_shadow": {
        "name": "NUM",
        "constraints": "-Infinity,Infinity,0,false"
    },
    "text": {
        "name": "TEXT"
    },
    "lists_get": {
        "name": "VAR"
    },
    "broadcast_input": {
        "name": "MESSAGE"
    },
    "get_audios": {
        "name": "sound_id"
    },
    "get_whole_audios": {
        "name": "sound_id"
    },
    "get_current_costume": {
        "name": "style_id"
    },
    "default_value": {
        "name": "TEXT",
        "has_been_edited": "false"
    },
    "get_current_scene": {
        "name": "scene"
    },
    "get_sensing_current_scene": {
        "name": "scene"
    }
}

# 参数默认值
SHADOW_FIELD_TEXT_MAP = {
    "math_number": "0",
    "controller_shadow": "0",
    "text": "",
    "lists_get": "?",
    "broadcast_input": "Hi",
    "get_audios": "?",
    "get_whole_audios": "all",
    "get_current_costume": "",
    "default_value": "0",
    "get_current_scene": "",
    "get_sensing_current_scene": ""
}

def createShadow(type, id=None, text=None):
    if type == "logic_empty":
        return f"<empty type=\"logic_empty\" id=\"{id}\" visible=\"visible\" editable=\"false\"></empty>"
    if id is None:
        id = randomBlockID()
    if text is None:
        text = SHADOW_FIELD_TEXT_MAP[type]
    attrs = SHADOW_FIELD_ATTRIBUTES_MAP[type]
    shadow = ElementTree.Element("shadow")
    shadow.set("type", type)
    shadow.set("id", id)
    shadow.set("visible", "visible")
    shadow.set("editable", "true")
    
    # 写入参数信息
    field = ElementTree.SubElement(shadow, "field")
    for name, value in attrs.items():
        field.set(name, value)
    field.text = str(text)

    return ElementTree.tostring(shadow, encoding='unicode')