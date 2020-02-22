import sys
import os
if sys.platform == 'win32':
    sys.path.append('thirdparty')
    os.environ['PATH'] = os.environ['PATH'] + './mdbtools-win/'
import functools
import glob
import shutil
import csv
from meza import io
import argparse

MDB_FOLDER = 'mdbs/'
OUT_FOLDER = 'outputs/'
OUT_SUMMARY = 'outputs/results.csv'
if sys.platform == 'win32':
    MDB_FOLDER = 'mdbs\\'
    OUT_FOLDER = 'outputs\\'

INCLUDED_COLUMN = ['Record', 'Charge', 'Date', 'BIN', 'Uoc', 'Isc', 'Rser', 'Rsh', 'FF', 'EFF', 'IRev1', 'IRev2']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    if sys.platform == 'win32':
        HEADER = OKBLUE = OKGREEN = WARNING = FAIL = ENDC = BOLD = UNDERLINE = ''

    @staticmethod
    def printc(color, string):
        print(color + string + bcolors.ENDC)

def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

class Mdb(object):
    def __init__(self, name, data=None):
        self._data = data if data != None else []
        self.bin_invalid = 0
        self.name = name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if len(data) == 0 or type(data[0]) is not dict:
             raise ValueError("invalid data!")
        self._data = data
        return

    def set_bin_invalid(self, invalid):
        self.bin_invalid = invalid

    def __write_to_csv(self):
        output_csv_name = OUT_FOLDER + self.name + '.csv'
        output = open(output_csv_name, 'w')
        bcolors.printc(bcolors.OKGREEN, 'write ' + output_csv_name + '...')
        writer = csv.DictWriter(output, fieldnames=list(self.data[0].keys()))

        writer.writeheader()
        for row in self.data:
            writer.writerow(row)
        output.close()
        return

    def read(self):
        name = self.name

        if len(name) < len(MDB_FOLDER) + len('.mdb') or name[-4:] != '.mdb' or name.index(MDB_FOLDER) != 0:
            raise ValueError("invalid name!")

        self.name = name[len(MDB_FOLDER):-4]
        bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'read ' + name + '...')
        #read mdb file
        try:
            for row in io.read(name):
                self._data.append(row)
        except:
            pass

    def write(self):
        return self.__write_to_csv()

    def summary(self):
        rc = {}
        keys = ['Uoc', 'Isc', 'Rser', 'Rsh', 'FF', 'EFF', 'IRev1', 'IRev2']

        rc['File'] = self.name
        rc['BIN invalid'] = self.bin_invalid
        rc['Number'] = len(self.data)
        for k in keys:
            res = [sub[k] for sub in self.data]
            res = list(map(float, res))
            rc[k] = sum(res) / len(res)
        return rc

def mdbp(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mdb = args[0]
        bcolors.printc(bcolors.OKGREEN, mdb.name + ' apply ' + str(func.__name__) + ' ...')
        return func(*args, **kwargs)
    return wrapper

@mdbp
def mdbp_filter_column(mdb):
    data = mdb.data
    rc = []
    for row in data:
        out_row = {k: v for k, v in row.items() if k in INCLUDED_COLUMN}
        rc.append(out_row)
    mdb.data = rc
    return mdb

@mdbp
def mdbp_select_charge(mdb):
    rc = []
    data = mdb.data

    charges = set()
    for row in data:
        if 'Charge' not in row:
            bcolors.printc(bcolors.FAIL, 'column Charge not found ')
            raise
        charges.add(row['Charge'])

    charges = list(charges)
    charges.sort(key=lambda x : len(x))
    shortest_len = len(charges[0])
    charges = [i for i in charges if len(i) == shortest_len]
    bcolors.printc(bcolors.OKGREEN, 'select charge:')
    for i in charges:
        bcolors.printc(bcolors.OKBLUE, i)

    for row in data:
        if row['Charge'] not in charges:
            continue
        rc.append(row)
    mdb.data = rc
    return mdb

@mdbp
def mdbp_filter_bin(mdb):
    rc = []
    data = mdb.data

    if len(data) == 0:
        return

    if 'BIN' not in data[0]:
        bcolors.printc(bcolors.FAIL, 'column BIN not found')
        raise

    count = 0
    for row in data:
        if 22 < float(row['BIN']):
            count = count + 1
            continue
        rc.append(row)
    bcolors.printc(bcolors.WARNING, 'BIN invalid: ' + str(count))
    mdb.set_bin_invalid(count)
    mdb.data = rc
    return mdb

test_counter = 0

@mdbp
def mdbp_filter_invalid_value(mdb):
    global test_counter
    keys = ['Uoc', 'Isc', 'Rser', 'Rsh', 'FF', 'EFF', 'IRev1', 'IRev2']
    rc = []
    data = mdb.data

    if len(data) == 0:
        return

    for k in keys:
        if k not in data[0]:
            bcolors.printc(bcolors.FAIL, 'column ' + k + ' not found')
            raise

    for row in data:
        invalid = False
        for k, v in row.items():
            if k not in keys:
                continue
            if not is_float(v) or float(v) < 0:
                invalid = True
                bcolors.printc(bcolors.WARNING, k + ':' + v + ' not valid')
                break
        if invalid:
            bcolors.printc(bcolors.WARNING, str(row) + ' Ignore')
            continue
        rc.append(row)

    mdb.data = rc
    test_counter = test_counter + 1
    return mdb

@mdbp
def mdbp_test_split(mdb):
    data = mdb.data
    data1 = data[0:5000]
    data2 = data[5000:]

    m1 = Mdb(mdb.name + '_A', data = data1)
    m2 = Mdb(mdb.name + '_B', data = data2)
    return [m1, m2]

@mdbp
def mdbp_test_split2(mdb):
    data = mdb.data
    data1 = data[0:2000]
    data2 = data[2000:]

    m1 = Mdb(mdb.name + '_A', data = data1)
    m2 = Mdb(mdb.name + '_B', data = data2)
    return [m1, m2]

class MdbPolicy(object):
    def __init__(self):
        self.policys = []

    def register(self, policy):
        self.policys.append(policy)

    def register_groups(self, policys):
        self.policys.extend(policys)

    def execute(self, mdb):
        self.mdb = [mdb, ]

        for index in range(len(self.policys)):
            mdbs = self.policys[index](mdb)
            if mdbs is mdb:
                continue
            if type(mdbs) is not list:
                raise ValueError("invalid data!")
            self.mdb = []
            for i in mdbs:
                p = MdbPolicy()
                p.register_groups(self.policys[index + 1:])
                self.mdb.extend(p.execute(i))
            break
        return self.mdb

def mdbp_get_from_file(name):
    policys = []
    return policys

def tiny_mdb(args):
    builtin_policys = [
        # mdbp_test_split,
        # mdbp_test_split2,
        mdbp_filter_column,
        mdbp_select_charge,
        mdbp_filter_bin,
        mdbp_filter_invalid_value,
    ]

    p = MdbPolicy()
    p.register_groups(builtin_policys if args.policy is None else mdbp_get_from_file(args.policy))

    summary = []
    for mdb in glob.glob(MDB_FOLDER + r'/*.mdb'):
        m = Mdb(mdb)
        m.read()
        n = p.execute(m)
        for i in n:
            i.write()
            summary.append(i.summary())

    if len(summary) == 0:
        return

    with open(OUT_SUMMARY, 'w', newline='') as f:
        bcolors.printc(bcolors.OKGREEN, 'write ' + OUT_SUMMARY + '...')
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

def cli_init():
    parser = argparse.ArgumentParser(description='Simple tool for mdb data processing.')
    parser.add_argument('-p', '--policy', nargs='?', help='specify policy file')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = cli_init()
    tiny_mdb(args)
