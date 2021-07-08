import os
import random
import datetime


class DiskManager:
    BLOCK_SIZE = 100
    ENTRY_LENGTH = 1500
    CREATE_DISK_COST = 0
    READ_BLOCK_COST = 10e-5
    DISK_SEEK_COST = 10e-7
    WRITE_BLOCK_COST = 10e-5

    def __init__(self):
        self.disks = dict()
        self.cost = 0
        self.scan_disks()

    def scan_disks(self) -> None:
        this_dir = os.getcwd()
        for file in os.listdir(this_dir):
            if file.endswith(".d"):
                file_name = file[:-2].split('_')
                self.disks[file_name[0]] = {
                    'path': file,
                    'size': int(file_name[1]),
                    'cursor': 0
                }

    def new(self, disk_name: str, disk_size: int) -> int:
        if disk_name in self.disks.keys():
            raise Exception('disk {} already exists!'.format(disk_name))

        self.disks[disk_name] = {
            'path': '{}_{}.d'.format(disk_name, disk_size),
            'size': disk_size,
            'cursor': 0
        }
        f = open("{}_{}.d".format(disk_name, disk_size), "x")  # returns error if file exists
        f.close()

        self.cost += self.CREATE_DISK_COST

        return 1

    def read_block(self, disk_name: str) -> list:
        self.check_disk_existence(disk_name)

        res = []
        f = open(self.disks[disk_name]['path'], "r")
        f.seek(self.disks[disk_name]['cursor'])

        for i in range(self.BLOCK_SIZE):
            line = f.readline()

            self.disks[disk_name]['cursor'] += 1 * self.ENTRY_LENGTH
            stripped_line = line.strip()[:-1].strip()

            if stripped_line == '':
                self.disks[disk_name]['cursor'] = f.tell()
                break
            res.append(stripped_line)

        f.close()

        self.cost += self.READ_BLOCK_COST

        return res

    def disk_seek(self, disk_name: str, delta: int) -> int:
        self.check_disk_existence(disk_name)

        cursor_position = self.disks[disk_name]['cursor'] + delta * self.ENTRY_LENGTH
        if (cursor_position < 0) or (self.disks[disk_name]['size'] * self.ENTRY_LENGTH < cursor_position):
            print(str(self.disks[disk_name]['size']) + " " + str(self.ENTRY_LENGTH) +" "+ str(cursor_position))
            raise Exception("seek amount is not in range of disk {}.d's size!".format(disk_name))

        self.disks[disk_name]['cursor'] = cursor_position

        self.cost += self.DISK_SEEK_COST

        return 1

    def write_block(self, disk_name: str, data: list) -> int:
        self.check_disk_existence(disk_name)

        data_length = len(data)
        if data_length > self.BLOCK_SIZE:
            raise Exception(
                "block size limit error:\n"
                "block size limit is {} lines "
                "but you tried to write {} lines! ".format(data_length, self.BLOCK_SIZE))

        normalized = []
        for d in data:
            d_length = len(d)
            diff = self.ENTRY_LENGTH - d_length - 2
            if diff < 0:
                raise Exception(
                    "line size limit error:\n"
                    "line size limit is {} characters "
                    "but you tried to write {} characters! ".format(d_length, self.ENTRY_LENGTH - 2))
            else:
                for i in range(diff):
                    d += " "
                d += "$"
                normalized.append(d)
        joined_data = '\r'.join(normalized) + '\r'
        f = open(self.disks[disk_name]['path'], "r+")
        f.seek(self.disks[disk_name]['cursor'])
        f.write(joined_data)
        self.disks[disk_name]['cursor'] = f.tell()
        f.close()
        self.cost += self.WRITE_BLOCK_COST

        return 1

    def get_cost(self) -> float:
        return self.cost

    def check_disk_existence(self, disk_name):
        if disk_name not in self.disks.keys():
            raise Exception('requested disk not exists!\n requested disk name: {}'.format(disk_name))
