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
            try:
                if line.startswith(self.code_create_new_account):
                    self.create_account(line.replace(self.code_create_new_account, "", 1))
                elif line.startswith(self.code_change_online_status):
                    self.change_online_status(line.replace(self.code_change_online_status, "", 1))
                elif line.startswith(self.code_follow_unfollow):
                    self.follow_unfollow(line.replace(self.code_follow_unfollow, "", 1))
                elif line.startswith(self.code_block_unblock):
                    self.block_unblock(line.replace(self.code_block_unblock, "", 1))
                elif line.startswith(self.code_find_online_friends):
                    self.find_online_friends(line.replace(self.code_find_online_friends, "", 1))
                elif line.startswith(self.code_recommend_accounts_to_follow):
                    self.recommend_new_accounts(line.replace(self.code_recommend_accounts_to_follow, "", 1))
                elif line.startswith("end"):
                    print(f"total cost is : {self.dm.cost}")
                else:
                    print(f"unknown command: {line}")
            except IndexError as e:
                print("error at line: {line} : {e}")

    def create_account(self, command):
        new_id, name, last_seen = command.split(" ")
        new_account_string = " ".join([new_id, name, "0", "online", last_seen])
        new_id = int(new_id)
        if self.cache.does_id_exist(new_id):
            print("this id already exists, please select a new one")
        else:
            self.cache.create_new_account(new_account=new_account_string,
                                          new_account_id=new_id)
        return

    def change_online_status(self, command):
        print(command.split(" "))
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
        return

    def block_unblock(self, command):
        id_1, id_2, block = command.split(" ")
        id_1, id_2 = int(id_1), int(id_2)
        block = False if block=="0" else True
        self.cache.block_unblock(id_1=id_1, id_2=id_2, block=block)
        return

    def follow_unfollow(self, command):
        id_1, id_2, follow = command.split(" ")
        id_1, id_2 = int(id_1), int(id_2)
        follow = False if follow == "0" else True
        self.cache.follow_unfollow(id_1=id_1, id_2=id_2, follow=follow)
        return

    def find_online_friends(self, command):
        account_id = int(command)
        self.cache.find_online_friends(account_id)
        return

    def recommend_new_accounts(self, command:str):
        command = command.split(" ")
        account_id, time = int(command[0]), int(command[1])
        # history = self.cache.get_recommend_history_string(account_id)
        # history = self.convert_string_to_history(history)
        history = {132:-1, 3533:-1, 7441:-1, 2671:-1, 5843:-1, 4590:-1}
        res, history = self.cache.recommend_new_accounts(account_id=account_id, time=time, recommend_history=history)
        # history = self.convert_history_to_string(account_id, history)
        print("recommended accounts  account:priority")
        for x in res:
            print(f"{x}")
        return

    def convert_history_to_string(self, account_id: int, history:dict):
        res = str(account_id)
        for x, y in history.items():
            res += " " + str(x) + ":" + str(y)
        return res

    def convert_string_to_history(self,history:str) -> dict:
        history = history.split(" ")
        res = {}
        history.pop(0)
        for line in history:
            x, y = line.split(":")
            x, y = int(x), int(y)
            res[x] = y
        return res
