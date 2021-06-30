from disk_manager import DiskManager
from challenge import Challenge
from shutil import copyfile #delete at the end
try:
    copyfile("dataset_backup", "dataset_100000.d") #regenereate the dataset- delete at the end
except:
    print("couldn't find the backup dataset. please insert dataset manually")
dm = DiskManager()

try:
    app = Challenge(dm)
    events_and_queries = []
    while True:
        line = input()
        if line == "end":
            break
        else:
            events_and_queries.append(line)

    app.run(events_and_queries)
finally:
    # dm.de_shuffle()
    pass
