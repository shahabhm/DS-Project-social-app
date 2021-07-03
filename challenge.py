from cache_manager import cache_manager


class Challenge:
    # region constants
    code_create_new_account = "0 1 "
    code_change_online_status = "0 2 "
    code_block_unblock = "0 3 "
    code_follow_unfollow = "0 4 "
    code_find_online_friends = "1 1 "
    code_recommend_accounts_to_follow = "1 2 "
    # endregion

    def __init__(self, disk_manager):
        self.dm = disk_manager
        self.cache = cache_manager(disk_manager=disk_manager)

    def run(self, events_or_queries):
        for line in events_or_queries:
            if line.startswith(self.code_create_new_account):
                self.create_account(line.replace(self.code_create_new_account, "", 1))
            elif line.startswith(self.code_change_online_status):
                self.change_online_status(line.replace(self.code_change_online_status,"",1))
            else:
                print("unknown command code")

    '''
    questinos:
    1- does this give an id already used?
    '''

    def create_account(self, command):
        new_id, name, last_seen = command.split(" ")
        if self.cache.does_id_exist(new_id):
            print("this id already exists, please select a new one")
        else:
            self.cache.create_new_account(new_account=" ".join([id, name, 0, "online", last_seen]),
                                          new_account_id=int(new_id))

    def change_online_status(self, command):
        account_id, online, last_seen = command.split(" ")
        if online == "0":
            online = False
        else:
            online = True
        account_id = int(account_id)
        if not self.cache.does_id_exist(account_id):
            print("this id does not exist")
        else:
            self.cache.change_online_status(account_id, online, last_seen)
