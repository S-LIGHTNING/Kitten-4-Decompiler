import json
import requests

from Tool import showError

API_GET_WORK_INFO = "https://api-creation.codemao.cn/kitten/r2/work/player/load/"

def getWorkInfo(workID):
    URL = API_GET_WORK_INFO + workID
    response = requests.get(URL)
    
    if response.status_code != 200:
        showError(f"获取作品信息失败，HTTP 状态码：{response.status_code}。", response.text)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        showError("解析作品信息数据失败。", response.text)
        
def getCompiledCode(workURL):
    URL = workURL
    response = requests.get(URL)
    
    if response.status_code != 200:
        showError(f"获取作品数据失败，HTTP 状态码：{response.status_code}。", response.text)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        showError("解析作品数据失败。", response.text)
