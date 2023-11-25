import json
import traceback

from CommunityAPI import *
from Decompiler import WorkDecompiler
from MetaData import *
from Tool import showError
from UI import *
from HTTP import HTTP

def main():
    printMetaData()

    workID = UI.askInteger("请输入作品 ID")

    workInfo = HTTP.getJSON(API_GET_RELEASED_WORK_INFO + str(workID))
    log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的信息。")

    compiledWork = HTTP.getJSON(workInfo["source_urls"][0])
    log(INFO, f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的编译文件。")

    try:
        decompiler = WorkDecompiler(workInfo, compiledWork)
        decompiler.onStart = lambda: log(INFO, f"开始反编译，作品名称：\033[4;32m{workInfo['name']}\033[0m。")
        def setActorLog(actor):
            actor.onPrepare = lambda: log(VERBOSE, f"正在准备角色 \033[4;32m{actor.actor['name']}\033[0m……")
            actor.onPrepareFunction = lambda name: log(VERBOSE, f"正在准备函数 \033[4;32m{name}\033[0m ……")
            actor.onStart = lambda: log(VERBOSE, f"正在反编译角色 \033[4;32m{actor.actor['name']}\033[0m……")
            actor.onStartFunction = lambda name: log(VERBOSE, f"正在反编译函数 \033[4;32m{name}\033[0m……")
        decompiler.onCreateActor = setActorLog
        decompiler.onPrepareActors = lambda: log(INFO, "正在准备角色……")
        decompiler.onStartActors = lambda: log(INFO, "正在反编译角色……")
        decompiler.onWritteWorkInfo = lambda: log(INFO, "正在清理……")
        decompiler.onClean = lambda: log(INFO, "正在写入作品信息……")
        decompiler.onFinish = lambda: log(INFO, "反编译完成。")
        decompiler.start()
    except:
        showError("反编译失败。", traceback.format_exc())
    saveSourceCode(compiledWork)

def saveSourceCode(sourceCode):
    input("按下回车键保存源码")
    while True:
        path = UI.askSaveFilePath(defaultType=".bcm", fileTypes=(("源码文件", ".bcm"), ("源码4文件", ".bcm4"), ("所有文件", ".*")))
        if path == "":
            if UI.askYesNot("要取消保存文件吗？"):
                print("已取消保存文件")
                return
        else:
            print(f"正在将源码保存到文件 \033[4m{path}\033[0m ……")
            try:
                with open(path, "w") as file:
                    json.dump(sourceCode, file)
                input("文件保存成功，按下回车键退出程序")
                return
            except Exception:
                log(ERROR, "保存失败，请尝试选择新的保存位置。")

if __name__ == "__main__":
    try:
        main()
    except:
        pass
