from HTTP import HTTP


API_GET_SOURCE_WORK_INFO = "https://api-creation.codemao.cn/kitten/work/ide/load/"
API_GET_KITTEN_RELEASED_WORK_INFO = "https://api-creation.codemao.cn/kitten/r2/work/player/load/"
API_GET_COCO_RELEASED_WORK_INFO = "https://api-creation.codemao.cn/kitten/r2/work/player/load/"

def getWorkInfo(workID):
    info = HTTP.getJSON(f"https://api.codemao.cn/creation-tools/v1/works/{workID}")
    return {
        "ID": info["id"],
        "name": info["work_name"],
        "type": info["type"],
        "version": info["bcm_version"],
        "author": {
            "ID": info["user_info"]["id"],
            "name": info["user_info"]["nickname"],
        }
    }

def getCompiledWorkURL(workInfo):
    return {
        "KITTEN4": lambda: HTTP.getJSON(f"https://api-creation.codemao.cn/kitten/r2/work/player/load/{workInfo['ID']}")["source_urls"][0],
        "KITTEN3": lambda: HTTP.getJSON(f"https://api-creation.codemao.cn/kitten/r2/work/player/load/{workInfo['ID']}")["source_urls"][0],
        "KITTEN2": lambda: HTTP.getJSON(f"https://api-creation.codemao.cn/kitten/r2/work/player/load/{workInfo['ID']}")["source_urls"][0],
        "COCO": lambda: HTTP.getJSON(f"https://api-creation.codemao.cn/coconut/web/work/{workInfo['ID']}/load")["data"]["bcmc_url"]
    }[workInfo["type"]]()
