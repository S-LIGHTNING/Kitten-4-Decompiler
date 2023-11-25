from datetime import datetime

VERBOSE = 0
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4

logLevel = INFO
logList = []

class Log:
    def __init__(self, level, message):
        self.time = datetime.now()
        self.level = level
        self.message = message

def log(level, message):
    log = Log(level, message)
    onLog(log)
    if level >= logLevel:
        showLog(log)

def onLog(log): pass
def showLog(log): pass
