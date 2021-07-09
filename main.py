from disk_manager import DiskManager
from challenge import Challenge
# delete at the end
from shutil import copyfile

try:
    copyfile("dataset_backup", "dataset_100000.d")  # regenerate the dataset- delete at the end
except:
    print("couldn't find the backup dataset. please insert dataset manually")
temporary = [
    "0 1 10001 hamed 1618497229",
    "0 1 10002 hamed 1618497229",
    "0 1 10003 hamed 1618497229",
    "0 1 10004 hamed 1618497229",
    "0 1 10005 hamed 1618497229",
    "0 1 10006 hamed 1618497229",
    "0 4 10001 10002 1",
    "0 4 10001 10003 1",
    "0 4 10001 10004 1",
    "0 4 10001 10005 1",
    "0 4 10002 10006 1",
    "0 4 10003 10006 1",
    "0 4 10004 10006 1",
    "0 4 10005 10006 1",
    "1 2 10001 1618497229",
    "end",
    "0 3 138 1 1",
    "0 3 4456 1 1",
    "0 3 9160 1 1",
    "0 3 279 1 1",
    "0 3 9030 1 1",
    "0 3 6164 1 1",
    "1 2 8740 1618497229",
    "0 2 10004 0 1618497229",
    "0 2 10006 0 1618497229",
    "0 2 10001 0 1618497229",
    "0 3 210 120 1",
    "0 3 120 210 1",
    "0 3 10001 10002 1",
    "0 3 205 210 1",
    "0 3 10001 10002 1",
    "0 3 210 120 0",
    "0 4 210 120 0",
    "0 4 1 10001 1",
    "0 4 1 10006 1",
    "0 4 999 1024 1",
    "0 3 500 600 1",
    "0 4 500 600 1",
    "0 4 600 500 1",
    "0 4 800 100 0",
    "0 4 2500 3500 1",
    "0 3 3500 2500 1",
    "0 4 10001 2133 1",
    "1 1 120",
    "1 1 10001",
    "1 1 1",
    "end"
]
dm = DiskManager()


#temporary = None
try:
    app = Challenge(dm)
    events_and_queries = []
    if temporary is not None:
        app.run(temporary)
        pass
    while True:
        line = input()
        if line == "end":
            break
        else:
            events_and_queries.append(line)
    app.run(events_and_queries)
finally:
    pass
