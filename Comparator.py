def compare(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return compareDict(a, b)
    # elif isinstance(a, list) and isinstance(b, list):
    #     return compareList(a, b)
    else:
        return b

def compareDict(a, b):
    add = {}
    delete = set()
    change = {}
    for key, value in b.items():
        if key in a:
            if value != a[key]:
                change[key] = compare(a[key], value)
        else:
            add[key] = value
    for key in a:
        if key not in b:
            delete.add(key)
    return {
        "add": add,
        "delete": delete,
        "change": change
    }

def compareList(a, b):
    pass

def similarity(a, b):
    if a == b: return 1
    elif isinstance(a, dict) and isinstance(b, dict):
        return dictSimilarity(a, b)
    elif isinstance(a, list) and isinstance(b, list):
        return listSimilarity(a, b)
    else:
        return 0

def dictSimilarity(a, b):
    diff = compareDict(a, b)
    change = len(diff["add"]) + len(diff["delete"]) + len(diff["change"])
    return 1 - change / (a.keys() + b.keys())

def listSimilarity(a, b):
    return 0

def merge(a, diff):
    if isinstance(a, dict):
        return mergeDict(a, diff)
    else:
        return diff

def mergeDict(a, diff):
    for key, value in diff["add"].items():
        a[key] = value
    for delete in diff["delete"]:
        try:
            del a[key]
        except UnboundLocalError:
            pass
    for key, value in diff["change"].items():
        try:
            a[key] = merge(a[key], value)
        except KeyError:
            pass
    return a
