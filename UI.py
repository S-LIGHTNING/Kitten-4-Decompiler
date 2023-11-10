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
                if value == "":
                    return default
                return int(value)
            except ValueError:
                print("输入有误，请重新输入！")
                
    def askYesNot(self, message, default=None):
        message += "(y/n)"
        if default == True:
            message += "[y]"
        elif default == False:
            message += "[n]"
        message += "："
        return input(message).lower() in {"y", "yes"} or default

    def askChoice(self, choices, message="请选择", default=None):
        length = len(choices)
        for count in range(length):
            print("{count}.{choices[count]}")
        while True:
            value = self.askInteger(message, default)
            if 0 < value and value <= length:
                return value
            else:
                print("输入有误，请重新输入！")
    
    def operate(self, operations):
        length = len(operations)
        operations.append({
            "name": "退出"
        })
        while True:
            try:
                choice = self.askChoice(operations, "请选择操作", length)
            except KeyboardInterrupt:
                return
            if choice == length:
                return
            else:
                operations[choice]["function"]()

    def showLog(self, log):
        print(log.message)

UI = CommandLineUserInterface()

log = Log.log
Log.showLog = UI.showLog
