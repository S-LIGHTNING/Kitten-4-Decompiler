import json
import requests

class HTTP:
    def getJSON(URL):
        return json.loads(HTTP.get(URL))
    def get(URL):
        response = requests.get(URL)
        if response.status_code != 200:
            raise Exception(f"HTTP 请求 {URL} 失败，状态码：{response.status_code}，响应：{response.text}。")
        return response.text
