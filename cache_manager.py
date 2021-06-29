import itertools

class cache_manager:

    most_accessed_accounts = {}
    most_accessed_accounts_limit = 50
    recently_created_accounts = {}
    recently_created_accounts_limit = 50
    cache_blocks = []
    dataset_accounts_count = 10000
    def __init__(self, disk_manager):
        self.dm = disk_manager
        pass

    def does_id_exist(self, new_id):
        pass

    def create_new_account(self, new_account_id, new_account):
        self.recently_created_accounts[new_account_id] = new_account
        if (len(self.recently_created_accounts)>self.recently_created_accounts_limit):
            res = []
            for i in range(1,int(self.recently_created_accounts_limit/2)):
                res.append(self.recently_created_accounts.get(self.dataset_accounts_count+i))
            self.dataset_accounts_count += self.recently_created_accounts_limit/2
            self.dm.seek(self.accounts_count - self.dm.disks["dataset"]['cursor']) #go to the end of the dataset
            self.dm.write("dataset" , res)