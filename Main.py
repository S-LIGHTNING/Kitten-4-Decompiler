import json
import tkinter
from tkinter import filedialog
import traceback
from CommunityAPI import getCompiledCode, getWorkInfo
from Decompiler import decompile
from MetaData import *
from Tool import showError

def main():
    printMetaData()
    
    workID = input("请输入作品 ID：")
    workInfo = getWorkInfo(workID)
    print(f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的信息。")
    workCompiledCode = getCompiledCode(workInfo["source_urls"][0])
    print(f"成功获取作品 \033[4;32m{workInfo['name']}\033[0m 的编译文件。")
    try:
        decompile(workInfo, workCompiledCode)
    except:
        showError("反编译失败。", traceback.format_exc())
    saveSourceCode(workCompiledCode)

def saveSourceCode(sourceCode):
    input("按下回车键保存源码")
    root = tkinter.Tk()
    root.title("保存源码文件")
    while True:
        path = filedialog.asksaveasfilename(defaultextension = ".bcm", filetypes = [("源码文件", ".bcm"), ("源码4文件", ".bcm4"), ("所有文件", ".*")])
        print(f"正在将源码保存到文件 \033[4m{path}\033[0m……")
        try:
            with open(path, "w") as file:
                json.dump(sourceCode, file)
            break
        except FileNotFoundError:
            print("\033[1;7;91m错误\033[0;1;91m：保存失败，请尝试选择新的保存位置。\033[0m")
    root.destroy()
    input("文件保存成功，按下回车键退出程序")

if __name__ == "__main__":
    main()