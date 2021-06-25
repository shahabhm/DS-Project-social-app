from disk_manager import DiskManager
from challenge import Challenge

dm = DiskManager()

try:
    app = Challenge(dm)

    events_and_queries = [
        "1 1 210"
        "0 1 10001 hamed 1618497229",
        "0 2 21 1 1618497229",
        "1 2 210 1618497229",
        "0 4 210 120 0",
        "0 3 210 120 0"
    ]

    app.run(events_and_queries)
finally:
    # dm.de_shuffle()
    pass
