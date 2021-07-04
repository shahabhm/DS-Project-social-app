import itertools
from account import account


class cache_manager:
    most_accessed_accounts = {}
    most_accessed_accounts_limit = 50
    recently_created_accounts = {}
    recently_created_accounts_limit = 50
    cache_block_0 = {}
    cache_block_1 = {}
    dirty_0: bool = False
    dirty_1: bool = False
    used_0 = 0
    used_1 = 0
    start_1 = 1
    start_0 = 1
    # note: we have to declare this for every account because an unblock need recalculating the whole dataset
    blocked_bloom = []
    # blocked bloom size is of order of one cache block
    dataset_accounts_count = 10000

    def __init__(self, disk_manager):
        self.dm = disk_manager

    def does_id_exist(self, new_id: int):
        return new_id < self.dataset_accounts_count

    def create_new_account(self, new_account_id, new_account: str):
        acc = account(new_account)
        if (len(self.recently_created_accounts) > self.recently_created_accounts_limit):
            res = []
            for i in range(1, int(self.recently_created_accounts_limit / 2)):
                res.append(self.recently_created_accounts.get(self.dataset_accounts_count + i))
            self.dataset_accounts_count += self.recently_created_accounts_limit / 2
            self.dm.disk_seek(
                self.dataset_accounts_count - self.dm.disks["dataset"]['cursor'])  # go to the end of the dataset
            self.dm.write_block("dataset", res)
        self.recently_created_accounts[new_account_id] = acc
        self.dataset_accounts_count += 1
        return

    def change_online_status(self, account_id: int, online: bool, last_seen: str):
        acc = self.find_account(account_id)
        acc.status = online
        if online:
            acc.last_seen = last_seen

    def find_account(self, id: int) -> account:
        res = None
        res = self.most_accessed_accounts.get(id)
        if res is not None:
            return res
        res = self.recently_created_accounts.get(id)
        if res is not None:
            return res
        res = self.cache_block_0.get(id)
        if res is not None:
            return res
        res = self.cache_block_1.get(id)
        if res is not None:
            return res
        self.update_cache(id)
        return self.find_account(id)

    def update_cache(self, id: int):
        if self.used_0 > 2 * self.used_1:
            if self.dirty_1:
                self.write_back(self.cache_block_1, start=self.start_1)
                self.dirty_1 = False
            self.cache_block_1 = self.fetch_block_for_id(id)
            self.used_0 /= 2
        elif self.used_1 > 2 * self.used_0:
            if self.dirty_0:
                self.write_back(self.cache_block_0, start=self.start_0)
                self.dirty_0 = False
            self.cache_block_0, self.start_0 = self.fetch_block_for_id(id)
            self.used_1 /= 2
        # two blocks are the same
        elif not self.dirty_0:
            self.cache_block_0, self.start_0 = self.fetch_block_for_id(id)
            self.used_0 = 0
        elif not self.dirty_1:
            self.cache_block_1, self.start_1 = self.fetch_block_for_id(id)
            self.used_1 = 0
        else:
            if self.used_0 > self.used_1:
                self.write_back(self.cache_block_1, start=self.start_1)
                self.cache_block_1, self.start_1 = self.fetch_block_for_id(id)

            else:
                self.write_back(self.cache_block_0, start=self.start_0)
                self.cache_block_0, self.start_0 = self.fetch_block_for_id(id)

    def write_back(self, cache_block: dict, start: int):
        res = []
        for user in cache_block.values():
            res.append(user)
        self.dm.disk_seek(start)
        self.dm.write_block(res)
        return

    # id_1 blocks/ unblocks id_2
    def block_unblock(self, id_1: int, id_2: int, block: bool):
        if block:
            # for blocked account
            acc = self.find_account(id_1)
            acc.connections.remove(str(id_2))
            acc.blocked.add(str(-id_2))
            self.update_bloom(acc)
            # now for blocked account
            acc = self.find_account(id_2)
            acc.connections.remove(str(id_1))
            acc.blocked_by.add("*" + str(id_1))
            self.blocked_bloom[id_1] = self.update_bloom(acc.blocked)
        else:
            pass

    def fetch_block_for_id(self, id: int):
        seek = id - 50
        if id < 50:
            seek = 0
        elif id > self.dataset_accounts_count - 50:
            seek = self.dataset_accounts_count - 100
        self.dm.seek(seek)
        return self.dm.read_block(), seek

    # this creates the bloom based on the blocked and blocker accounts for an account
    def update_bloom(self, acc:account):
        pass
