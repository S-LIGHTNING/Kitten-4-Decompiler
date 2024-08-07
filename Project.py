import json
import os
import shutil
from playwright.sync_api import sync_playwright
import requests

from CommunityAPI import *
from Comparator import compare, merge
from KittenDecompiler import KittenWorkDecompiler
from HTTP import HTTP
from Tool import showError
from UI import *

def main():
    UI.operate([
        {
            "name": "新建项目",
            "function": askNewProject
        }, {
            "name": "打开项目",
            "function": askOpenProject
        }, {
            "name": "删除项目",
            "function": askDeleteProject
        }
    ], default=1)

def askNewProject():
    dir = UI.askDirectory("选择项目位置")
    if os.path.exists(f"{dir}\\配置.json"):
        if UI.askYesNot("项目已存在，是否打开？"):
            openProject(dir)
        return
    config = {
        "source_work": UI.askInteger("请输入源作品 ID")
    }
    project = Project(dir, config)
    project.init()
    project.operate()

def askOpenProject():
    openProject(UI.askDirectory("打开一个项目"))

def openProject(dir):
    log(INFO, f"正在打开项目 \033[4;32m{dir}\033[0m ……")
    try:
        with open(f"{dir}\\配置.json", "r") as file:
            log(VERBOSE, "正在加载项目配置……")
            config = json.load(file)
    except Exception as e:
        log(ERROR, "打开项目失败！")
        return
    Project(dir, config).operate()

def askDeleteProject():
    deleteProject(UI.askDirectory("请选择要删除的项目"))

def deleteProject(dir):
    os.remove(f"{dir}\\配置.json")
    os.remove(f"{dir}\\原源码.bcm")
    os.remove(f"{dir}\\上次\\")
    os.remove(f"{dir}\\源码.bcm")

class Project:

    def __init__(self, dir, config):
        self.dir = dir
        self.config = config

    def init(self):
        workInfo = HTTP.getJSON(API_GET_KITTEN_RELEASED_WORK_INFO + str(self.sourceWork))
        log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的信息。")

        compiledWork = HTTP.getJSON(workInfo["source_urls"][0])
        log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的编译文件。")

        self.name = workInfo['name']
        with open(f"{self.dir}\\原源码.bcm", "w") as file:
            json.dump(KittenWorkDecompiler(workInfo, compiledWork).start(), file)
        shutil.copyfile(f"{self.dir}\\原源码.bcm", f"{self.dir}\\源码.bcm")

        self.cloudWorkID = None
        self.sourceCloudWorkID = None

        log(INFO, f"项目 \033[4;32m{self.name}\033[0m 初始化完成。")

    def updateSourceChanges(self):
        workInfo = HTTP.getJSON(API_GET_KITTEN_RELEASED_WORK_INFO + str(self.sourceWork))
        log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的信息。")

        compiledWork = HTTP.getJSON(workInfo["source_urls"][0])
        log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的编译文件。")

        with open(f"{self.dir}\\原源码.bcm", "r") as file:
            old = json.load(file)
        new = KittenWorkDecompiler(workInfo, compiledWork).start()
        with open(f"{self.dir}\\源码.bcm", "r", encoding='utf-8') as file:
            edited = json.load(file)

        log(INFO, f"正在查找原作品更改……")
        diff = compare(old, new)
        log(INFO, f"正在合并原作品更改……")
        edited = merge(edited, diff)

        log(INFO, f"正在备份……")
        os.mkdir(f"{self.dir}\\备份")
        os.rename(f"{self.dir}\\原源码.bcm", f"{self.dir}\\备份\\原源码.bcm")
        os.rename(f"{self.dir}\\源码.bcm", f"{self.dir}\\备份\\源码.bcm")
        if os.path.exists(f"{self.dir}\\上次"):
            os.rename(f"{self.dir}\\上次", f"{self.dir}\\备份\\上次")
        os.rename(f"{self.dir}\\备份", f"{self.dir}\\上次")

        log(INFO, f"正在写入更改……")
        log(VERBOSE, f"正在更新写入原源码文件……")
        with open(f"{self.dir}\\原源码.bcm", "w") as file:
            json.dump(new, file)
        log(VERBOSE, f"正在更新写入源码文件……")
        with open(f"{self.dir}\\源码.bcm", "w") as file:
            json.dump(edited, file)

    def openKitten(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            def modify(route, request):
                print(f"成功拦截到作品信息请求。")
                response = route.fetch()
                route.fulfill(
                    response = response,
                    body = {
                        "name": self.name,
                        "preview": "",
                        "source_urls": [
                            "https://codemao.cn/work/file.bcm4"
                        ],
                        "ide_type": "KITTEN",
                        "updated_time": 1699627419,
                        "version": "4.11.10",
                        "published_status": 0,
                        "work_source_label": 0,
                        "role": 1,
                        "is_coll_work": False,
                        "work_business": 0
                    },headers = {**response.headers, "content-type": "application/json;charset=UTF-8"},
                )
            def modifyWork(route, request):
                print(f"成功拦截到作品代码请求。")
                route.fulfill(path=f"{self.dir}\\原源码.bcm")
            page.route("**/kitten/work/ide/load/{self.sourceWork}", modify)
            page.route("**/work/file.bcm4", modifyWork)
            page.goto(f"https://kitten4.codemao.cn/#{self.sourceWork}")
            input("按下回车键退出浏览器")

    def operate(self):
        UI.operate([
            {
                "name": "合并源作品更新",
                "function": self.updateSourceChanges
            }, {
                "name": "撤销上次源作品更新合并",
                "function": lambda: print("无效操作")
            }, {
                "name": "更新发布作品",
                "function": lambda: print("无效操作")
            }, {
                "name": "伪装原作品打开源码编辑器",
                "function": self.openKitten
            }, {
                "name": "修改项目配置",
                "function": self.editConfig
            }
        ], default=0)

    def editConfig(self):
        def setName():
            self.name = UI.askString("请输入新的名称", self.name)
        def setSourceWork():
            self.name = UI.askInteger("请输入源作品 ID", self.sourceWork)
        operations = [
            {
                "name": f"修改项目名称（当前为：{self.name}）",
                "function": setName
            }, {
                "name": f"修改源作品（当前为：{self.sourceWork}）",
                "function": setSourceWork
            }
        ]
        if self.cloudWorkID is not None:
            operations.append({
                "name": f"转为本地作品（当前云端作品：{self.cloudWorkID}）",
                "function": lambda: print("无效操作")
            })
            if self.sourceCloudWorkID is not None:
                operations.append({
                    "name": "取消绑定源云云端作品（已绑定：{self.sourceCloudWork}）",
                    "function": lambda: print("无效操作")
                })
            else:
                operations.append({
                    "name": "创建/绑定源云云端作品",
                    "function": lambda: print("无效操作")
                })
        else:
            operations.append({
                "name": "转为云端作品",
                "function": lambda: print("无效操作")
            })
        UI.operate(operations)

    @property
    def name(self):
        return self.config["name"]
    @name.setter
    def name(self, value):
        self.config["name"] = value
        self.writeConfig()

    @property
    def sourceWork(self):
        return self.config["source_work"]
    @sourceWork.setter
    def sourceWork(self, value):
        self.config["source_work"] = value
        self.writeConfig()

    @property
    def cloudWorkID(self):
        return self.config["cloud_work"]
    @cloudWorkID.setter
    def cloudWorkID(self, value):
        self.config["cloud_work"] = value
        self.writeConfig()

    @property
    def sourceCloudWorkID(self):
        return self.config["source_cloud_work"]
    @sourceCloudWorkID.setter
    def sourceCloudWorkID(self, value):
        self.config["source_cloud_work"] = value
        self.writeConfig()

    @property
    def cloudWork(self):
        workInfo = HTTP.getJSON(API_GET_SOURCE_WORK_INFO + str(self.cloudWorkID))
        log(VERBOSE, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的信息。")
        work = HTTP.getJSON(workInfo["source_urls"][0])
        log(VERBOSE, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的数据。")
        return work
    @cloudWork.setter
    def cloudWork(self, value):
        pass

    @property
    def sourceCloudWork(self):
        return self.config["source_cloud_work"]
    @sourceCloudWork.setter
    def sourceCloudWork(self, value):
        self.config["source_cloud_work"] = value
        self.writeConfig()

    def writeConfig(self):
        with open(f"{self.dir}\\配置.json", "w") as file:
            json.dump(self.config, file)

if __name__ == "__main__":
    main()
