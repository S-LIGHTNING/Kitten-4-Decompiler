from xml.etree import ElementTree

from Tool import randomBlockID

SHADOW_ALL_TYPES = {
    "math_number",
    "text",
    "lists_get",
    "broadcast_input",
    "get_audios",
    "get_current_costume",
    "default_value"
}
SHADOW_FIELD_ATTRIBUTES_MAP = {
    "math_number": {
        "name": "NUM",
        "constraints": "-Infinity,Infinity,0,",
        "allow_text": "true"
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
    "get_current_costume": {
        "name": "style_id"
    },
    "default_value": {
        "name": "TEXT",
        "has_been_edited": "false"
    }
}
SHADOW_FIELD_TEXT_MAP = {
    "math_number": "0",
    "text": "",
    "lists_get": "?",
    "broadcast_input": "Hi",
    "get_audios": "?",
    "get_current_costume": "",
    "default_value": "0"
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
    field = ElementTree.SubElement(shadow, "field")
    for name, value in attrs.items():
        field.set(name, value)
    field.text = text
    return ElementTree.tostring(shadow, encoding='unicode')