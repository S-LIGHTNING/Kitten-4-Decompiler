import tkinter
from tkinter import filedialog
from Log import VERBOSE, DEBUG, INFO, WARNING, ERROR
import Log

class CommandLineUserInterface:

    def __init__(self):
        pass

    def askInteger(self, message="请输入整数", default=None):
        if default is not None:
            message += f"[{default}]"
        message += "："
        while True:
            try:
                value = input(message)
                if default is not None and value == "":
                    return default
                return int(value)
            except ValueError:
                print("输入有误，请重新输入！")

    def askString(self, message="请输入内容", default=None):
        if default is not None:
            message += f"[{default}]"
        message += "："
        value = input(message)
        if default is not None and value == "":
            return default
        return value
                
    def askYesNot(self, message="确定？", default=None):
        message += "(y/n)"
        if default == True:
            message += "[y]"
        elif default == False:
            message += "[n]"
        message += "："
        return input(message).lower() in {"y", "yes"} or default

    def askChoice(self, choices, message="请选择", default=None):
        print()
        length = len(choices)
        for count in range(length):
            print(f"{count + 1}.{choices[count]}")
        while True:
            value = self.askInteger(message, default + 1)
            if 0 < value and value <= length:
                return value - 1
            else:
                print("输入有误，请重新输入！")
    
    def operate(self, operations, default=None):
        length = len(operations)
        operations.append({
            "name": "退出"
        })
        if default is None: default = length
        while True:
            try:
                choice = self.askChoice([operation["name"] for operation in operations], "请选择操作", default)
            except KeyboardInterrupt:
                return
            if choice == length:
                return
            else:
                operations[choice]["function"]()

    def askFilePath(self, message="请选择一个文件", fileTypes=(), default=None):
        root = tkinter.Tk()
        root.title(message)
        path = filedialog.askopenfilename(filetypes=fileTypes, title=message)
        root.destroy()
        if default is not None and path == "":
            return default
        return path

    def askDirectory(self, message="请选择一个文件夹", default=None):
        root = tkinter.Tk()
        root.title(message)
        path = filedialog.askdirectory(title=message)
        root.destroy()
        if default is not None and path == "":
            return default
        return path

    def askSaveFilePath(self, message="请选择文件保存位置", defaultType=None, fileTypes=(), default=None):
        root = tkinter.Tk()
        root.title(message)
        path = filedialog.asksaveasfilename(defaultextension=defaultType, filetypes=fileTypes, title=message)
        root.destroy()
        if default is not None and path == "":
            return default
        return path

    def showLog(self, log):
        if log.level == WARNING:
            print(f"\033[1;7;93m警告\033[0;1;93m：{log.message}\033[0m")
        elif  log.level == ERROR:
            print(f"\033[1;7;91m错误\033[0;1;91m：{log.message}\033[0m")
        else:
            print(log.message)

UI = CommandLineUserInterface()

log = Log.log
Log.showLog = UI.showLog
