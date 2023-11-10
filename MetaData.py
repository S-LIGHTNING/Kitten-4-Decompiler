class PROJECT:
    NAME = "源码编辑器4反编译器"
    VERSIONS = "1.0.0"
    class AUTHOR:
        NAME = "SLIGHTNING"

def printMetaData():
    print(PROJECT.NAME)
    print(f"欢迎使用 \033[4;94m{PROJECT.NAME}\033[0m {PROJECT.VERSIONS} 版本。")
    print(f"该软件由 \033[4;94m{PROJECT.AUTHOR.NAME}\033[0m 开发。")
    print("\033[1;3;5;7;91m该软件严禁用于违法用途！\033[0m")
    input("按下回车键继续")
