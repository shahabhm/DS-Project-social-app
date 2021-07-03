from disk_manager import DiskManager
from challenge import Challenge
# delete at the end
from shutil import copyfile

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
        elif line == "save end":
            # app.cache.dump() // in case we needed to save the cached data before exit
            pass
        else:
            events_and_queries.append(line)

    app.run(events_and_queries)
finally:
    pass
