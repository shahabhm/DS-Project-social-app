# this class is supposed to hold data for accounts in the memory

class account:

    # creates account object from data line in database
    # couldn't make multiple constructors
    def __init__(self, data: str):
        data = data.split(" ")
        self.id = int(data[0])
        self.name = data[1]
        self.last_seen = int(data[-1])
        if data[-2] == "online":
            self.status = False
        else:
            self.status = True
        self.connections = set()
        self.blocked = set()
        self.blocked_by = set()
        for relation in data[2:-3]:
            if relation.startswith("-"):
                self.blocked.add(relation)
            elif relation.startswith("*"):  # means this is blocked by another account
                self.blocked_by.add(relation)
            else:
                self.connections.add(relation)

    def __hash__(self):
        # necessary for instances to behave sanely in dicts and sets.
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        if self.status:
            online = " online "
        else:
            online = " offline "
        return str(self.id) + " " + self.name + " ".join(self.connections) +\
               " -".join(self.blocked) + " *".join(self.blocked_by) + online + str(self.last_seen)
