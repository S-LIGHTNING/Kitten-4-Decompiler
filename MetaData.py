class PROJECT:
    NAME = "源码反编译器4"
    VERSIONS = "1.0.3"
    class AUTHOR:
        NAME = "SLIGHTNING"

def printMetaData():
    print(PROJECT.NAME)
    print(f"欢迎使用 \033[4;94m{PROJECT.NAME}\033[0m {PROJECT.VERSIONS} 版本。")
    print(f"该软件由 \033[4;94m{PROJECT.AUTHOR.NAME}\033[0m 开发。")
    with open("许可.txt", "r", encoding="UTF-8") as file:
        while line := file.readline():
            if line[-1] == "\n": line = line[0: len(line) - 1]
            print(f"\033[1;5;7;91m{line}\033[0m")
            input("按下回车键继续")
