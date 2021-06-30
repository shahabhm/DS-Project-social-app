class Challenge:
    def __init__(self, disk_manager):
        self.dm = disk_manager

    def run(self, events_and_queries):
        """
        input is an array of strings, consisting events and queries.
        e.g. [
                "1 1 210"
                "0 1 10001 hamed 1618497229",
                "0 2 21 1 1618497229",
                "1 2 210 1618497229",
                "0 4 210 120 0",
                "0 3 210 120 0"
            ]
        """

        # remove following lines in developing, these lines are for getting familiar with the system

        # print all disks that we have
        print(self.dm.disks)

        # reading first block
        first_block = self.dm.read_block('dataset')
        for line in first_block:
            print(line)

        print('finished reading first block => now we are at first of line: 101')

        # seeking to previous line
        self.dm.disk_seek('dataset', delta=-1)
        print('seeking to previous line => now we are at first of line: 100')

        print('writing i')
        self.dm.write_block('dataset', first_block[0:10])
        print('writing two lines into line 100 % 101 () => now we are at first of line: 102')
        print('note that we are allowed to write 100 lines (block_size) into the whole block starting from line 100, ')
        print('but here we just replace two lines.')

        # important: use a copy of dataset, because we have damaged the dataset
        print('congratulations! we just have ruined our dataset because of careless writing into our dataset!')
        print('use a new copy of dataset!')
