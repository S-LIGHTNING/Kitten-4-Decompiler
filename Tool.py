import random

def askYesNot(text):
    return input(f"{text}(y/n)：").lower() in {"y", "yes"}

def showError(info):
    last = info.split('\n')[-2]
    print(f"\033[1;7;91m错误\033[0;1;91m：{last}\033[0m")
    if askYesNot("是否查看更多信息？"):
        print(f"\033[0;1;91m{info}\033[0m")
        input("按下回车键退出程序")

def randomBlockID():
    return ''.join([random.choice('0123456789abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ') for i in range(20)])
