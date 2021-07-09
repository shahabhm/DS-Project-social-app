from account import account
from bloom_filter2 import BloomFilter
import heapq


class cache_manager:
    most_accessed_accounts = {}
    most_accessed_accounts_limit = 25
    recently_created_accounts = {}
    recently_created_accounts_limit = 10
    recommend_new_friend_crawler_limit = 5000
    recommend_new_friend_result_limit = 20
    ten_days_epoch = 10 * 24 * 60 * 60
    cache_block_0 = {}
    cache_block_1 = {}
    dirty_0: bool = False
    dirty_1: bool = False
    locked_0: bool = False
    locked_1: bool = False
    start_0 = 0
    start_1 = 0

    # note: we have to declare this for every account because an unblock need recalculating the whole dataset
    blocked_bloom = []
    # blocked bloom size is of order of one cache block
    dataset_accounts_count = 10000

    def __init__(self, disk_manager):
        self.dm = disk_manager
        for i in range(0, self.dataset_accounts_count):
            self.blocked_bloom.append(BloomFilter(max_elements=11000, error_rate=0.1))
        # self.initialize_most_used_accounts()
        #  self.recommend_cache = disk_manager.new("recommend", 100000)
        # for i in range(0, 101):
        #     res = []
        #     for j in range(1, 101):
        #         res.append(str(100 * i + j))
        #     disk_manager.write_block("recommend", res)

    # tested
    def does_id_exist(self, new_id: int):
        return new_id <= self.dataset_accounts_count + len(self.recently_created_accounts)

    # tested
    def create_new_account(self, new_account_id: int, new_account: str):
        acc = account(new_account)
        if len(self.recently_created_accounts) > self.recently_created_accounts_limit / 2:
            overflow_amount = int(self.recently_created_accounts_limit / 2)
            res = []
            for i in range(self.dataset_accounts_count + 1, self.dataset_accounts_count + overflow_amount + 1):
                temp = str(self.recently_created_accounts.pop(i))
                res.append(temp)
                print("removing account from cache: " + temp)
            self.blocked_bloom.append(BloomFilter(11000,0.1))
            # for i in range(1, int(self.recently_created_accounts_limit / 2)):
            #     res.append(self.recently_created_accounts.get(self.dataset_accounts_count + i))
            # self.dm.disk_seek(disk_name="dataset", delta=
            # self.dataset_accounts_count - self.dm.disks["dataset"]['cursor']/self.dm.ENTRY_LENGTH)  # go to the end of the dataset
            self.seek_line(line=self.dataset_accounts_count, disk="dataset")
            self.dm.write_block("dataset", res)
            self.dataset_accounts_count += overflow_amount

        self.recently_created_accounts[new_account_id] = acc

        return

    # tested for recently created
    def change_online_status(self, account_id: int, online: bool, last_seen: str):
        acc = self.find_account(account_id, dirty=True, lock=False)
        acc.status = online
        if online:
            acc.last_seen = last_seen

    def find_account(self, acc_id: int, lock: bool, dirty: bool) -> account:
        if acc_id in self.most_accessed_accounts:
            return self.most_accessed_accounts[acc_id]
        if acc_id in self.recently_created_accounts:
            return self.recently_created_accounts[acc_id]
        if acc_id in self.cache_block_0:
            if lock:
                self.locked_0 = True
                self.locked_1 = False
            if dirty:
                self.dirty_0 = True
            return self.cache_block_0[acc_id]
        if acc_id in self.cache_block_1:
            if lock:
                self.locked_1 = True
                self.locked_0 = False
            if dirty:
                self.dirty_1 = True
            return self.cache_block_1[acc_id]
        self.update_cache(acc_id)
        return self.find_account(acc_id, lock, dirty)

    # note: cache_block 0 is static and block 1 will be replaced
    def update_cache(self, acc_id: int):
        if self.locked_0:
            if self.dirty_1:
                self.write_back(self.cache_block_1, start=self.start_1)
                self.dirty_1 = False
                self.locked_1 = False
            self.cache_block_1, self.start_1 = self.fetch_block_for_id(acc_id)
        elif self.locked_1:
            if self.dirty_0:
                self.write_back(self.cache_block_0, start=self.start_0)
                self.dirty_0 = False
                self.locked_0 = False
            self.cache_block_0, self.start_0 = self.fetch_block_for_id(acc_id)
        # two blocks are the same
        elif not self.dirty_0:
            self.cache_block_0, self.start_0 = self.fetch_block_for_id(acc_id)
        elif not self.dirty_1:
            self.cache_block_1, self.start_1 = self.fetch_block_for_id(acc_id)
        else:
            self.write_back(self.cache_block_0, start=self.start_0)
            self.cache_block_0, self.start_0 = self.fetch_block_for_id(acc_id)

    def write_back(self, cache_block: dict, start: int):
        res = []
        for user in cache_block.values():
            res.append(str(user))
        self.seek_line("dataset", start)
        self.dm.write_block(disk_name="dataset", data=res)
        return

    # id_1 blocks/ unblocks id_2
    def block_unblock(self, id_1: int, id_2: int, block: bool):
        if block:
            # for blocked account
            acc = self.find_account(id_1, lock=True, dirty=True)
            try:
                acc.connections.remove(str(id_2))
            except:
                pass
            acc.blocked.add(str(-id_2))
            self.update_bloom(acc)
            # now for blocked account
            acc = self.find_account(id_2, lock=True, dirty=True)
            try:
                acc.connections.remove(str(id_1))
            except:
                pass
            # self.blocked_bloom[id_1] = self.update_bloom(acc.blocked)
        else:
            acc = self.find_account(id_1, lock=True, dirty=True)
            try:
                acc.blocked.remove(str(-id_2))
            except:
                pass
            self.update_bloom(acc)
            # now for blocked account

    def fetch_block_for_id(self, id: int):
        seek = id - 50
        if id < 50:
            seek = 0
        elif id > self.dataset_accounts_count - 50:
            seek = self.dataset_accounts_count - 100
        self.seek_line(disk="dataset", line=seek)
        res = {}
        temp = self.dm.read_block("dataset")
        for i in range(0, len(temp)):
            res[seek + i + 1] = account(temp[i])
        return res, seek

    # this creates the bloom based on the blocked and blocker accounts for an account
    def update_bloom(self, acc: account):
        new_bloom = BloomFilter(max_elements=11000, error_rate=0.1)
        for blc in acc.blocked:
            new_bloom.add(-int(blc))
        self.blocked_bloom[acc.id-1] = new_bloom

    # true if dest blocked acc
    def is_blocked(self, blocker: int, blocked: int) -> bool:
        try:
            assert blocked in self.blocked_bloom[blocker-1]
        except:
            return False
        acc = self.find_account(blocker, lock=False, dirty=False)
        if acc.blocked.__contains__(str(-blocked)):
            return True
        return False

    def follow_unfollow(self, id_1: int, id_2: int, follow: bool):
        acc = self.find_account(acc_id=id_1, lock=True, dirty=True)
        if follow:
            if self.is_blocked(id_1, id_2):
                print("can't follow: you have blocked this user")
            elif self.is_blocked(blocker=id_2, blocked=id_1):
                print("can't follow: you have been blocked by this user")
            else:
                try:
                    acc.connections.add(str(id_2))
                    if str(id_2) == "":
                        print("error")
                except:
                    print(f"there was a problem account {id_1} could'nt follow {id_2}")
        else:  # unfollow
            try:
                acc.connections.add(str(id_2))
            except:
                pass
                # print(f"there was a problem unfollowing {id_1} , {id_2}")

    def find_online_friends(self, account_id: int):
        acc = self.find_account(account_id, lock=False, dirty=False)
        online = []
        offline = []
        for friend in acc.connections:
            try:
                friend_acc = self.find_account(int(friend), lock=False, dirty=False)
                if friend_acc.status:
                    online.append(friend)
                else:
                    offline.append(friend)
            except:
                print("error in finding friend account")
        print(f"online friends of account {acc.id} are : {online}")
        print(f"offline friends of account {acc.id} are : {offline}")
        return

    def recommend_new_accounts(self, account_id: int, time: int, recommend_history: dict):
        acc = self.find_account(acc_id=account_id, lock=False, dirty=False)
        res = {}
        new_declines = {}
        for friend in acc.connections:
            friend_acc = self.find_account(int(friend), lock=False, dirty=False)
            for person in friend_acc.connections:
                person = int(person)
                if acc.blocked.__contains__(-person) or acc.connections.__contains__(
                        person):  # this person has been blocked or is followed
                    continue
                if person == account_id:
                    continue
                temp_acc = self.find_account(person, lock=False, dirty=False)
                if self.is_blocked(person, account_id):
                    pass  # this person blocked the account
                elif person in recommend_history:
                    if recommend_history[person] == -1:
                        pass
                    if recommend_history[person] - time > self.ten_days_epoch:
                        recommend_history[person] = -1
                        pass
                    else:
                        res[person] = self.calculate_adj_score(acc_1=acc, acc_2=friend_acc, acc_3=temp_acc)
                elif person in res:
                    res[person] += self.calculate_adj_score(acc_1=acc, acc_2=friend_acc, acc_3=temp_acc)
                    recommend_history[person] = time
                else:
                    res[person] = self.calculate_adj_score(acc_1=acc, acc_2=friend_acc, acc_3=temp_acc)
                    recommend_history[person] = time
            if len(res) > self.recommend_new_friend_crawler_limit:
                break
        ans = []
        for x in {key: value for key, value in res.items() if
                  value in heapq.nlargest(10, res.values())}:
            if len(ans) > 5:
                if res[x] == 1:
                    continue
            ans.append((x, res[x]))
        return ans, recommend_history

    def seek_line(self, disk: str, line: int):
        self.dm.disk_seek(disk, line - self.dm.disks["dataset"]['cursor'] / self.dm.ENTRY_LENGTH)

    def initialize_most_used_accounts(self):
        temp = {}
        for i in range(1, self.dataset_accounts_count + 1):
            temp[i] = 0
        for i in range(0, 100):
            for line in self.dm.read_block("dataset"):
                acc = account(line)
                temp[acc.id] += len(acc.connections)
                for connection in acc.connections:
                    if int(connection) > 0:
                        temp[int(connection)] += 1
        for x in {key: value for key, value in temp.items() if value in heapq.nlargest(self.most_accessed_accounts_limit
                , temp.values())}:
            self.most_accessed_accounts[x] = self.find_account(x, lock=False, dirty=False)
        pass

    def get_recommend_history_string(self, account_id) -> str:
        self.seek_line("recommend", account_id)
        return self.dm.read_block(account_id)[0]  # we only need one line of this

    def set_recommend_history_string(self, account_id, string: str):
        data = [string]
        self.dm.write_block(disk_name="recommend", data=data)

    def calculate_adj_score(self, acc_1: account, acc_2: account, acc_3: account) -> int:
        score = 1
        if acc_3.connections.__contains__(str(acc_1.id)):
            score += 3
        if acc_3.connections.__contains__(str(acc_2.id)):
            score += 2
        if acc_2.connections.__contains__(str(acc_1.id)):
            score += 5
        return score
