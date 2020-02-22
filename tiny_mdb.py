import sys
import os
if sys.platform == 'win32':
    sys.path.append('thirdparty')
    os.environ['PATH'] = os.environ['PATH'] + './mdbtools-win/'
import glob
import shutil
import csv
from meza import io

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

def mdbp_common(data, mdb, policy):
    if len(data) == 0:
        return

    if type(data[0]) is not dict:
        rc = []
        for sub in data:
            rc.append(mdbp_common(sub, mdb, policy))
        return rc

    return policy(data, mdb)

def __mdbp_filter_column(data, mdb):
    rc = []
    for row in data:
        out_row = {k: v for k, v in row.items() if k in INCLUDED_COLUMN}
        rc.append(out_row)
    return rc

def mdbp_filter_column(data, mdb):
    return mdbp_common(data, mdb, __mdbp_filter_column)

def __mdbp_select_charge(data, mdb):
    rc = []

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
    return rc

def mdbp_select_charge(data, mdb):
    return mdbp_common(data, mdb, __mdbp_select_charge)

def __mdbp_filter_bin(data, mdb):
    rc = []
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
    return rc

def mdbp_filter_bin(data, mdb):
    return mdbp_common(data, mdb, __mdbp_filter_bin)

def __mdbp_filter_invalid_value(data, mdb):
    keys = ['Uoc', 'Isc', 'Rser', 'Rsh', 'FF', 'EFF', 'IRev1', 'IRev2']
    rc = []

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

    return rc

def mdbp_filter_zero_negative_value(data, mdb):
    return mdbp_common(data, mdb, __mdbp_filter_invalid_value)

class MdbPolicy(object):
    def __init__(self):
        self.policys = []

    def register(self, policy):
        self.policys.append(policy)

    def register_groups(self, policys):
        self.policys.extend(policys)

    def execute(self, data, mdb):
        for policy in self.policys:
            data = policy(data, mdb)
        return data

class Mdb(object):
    # TODO: support multiplie demension
    def __init__(self, name, policy):
        self.data = []
        self.policy = policy
        self.bin_invalid = 0

        if len(name) < len(MDB_FOLDER) + len('.mdb') or name[-4:] != '.mdb' or name.index(MDB_FOLDER) != 0:
            print('invalid mdb file')
            raise

        self.name = name[len(MDB_FOLDER):-4]
        bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'read ' + name + '...')
        #read mdb file
        try:
            for row in io.read(name):
                self.data.append(row)
        except:
            pass

    def process(self):
        if self.policy is None:
            return
        self.data = self.policy.execute(self.data, self)

    def set_bin_invalid(self, invalid):
        self.bin_invalid = invalid

    def write_to_csv(self, output_name, data):
        if len(data) == 0:
            return
        if type(data[0]) is dict:
            output_csv_name = OUT_FOLDER + output_name + '.csv'
            output = open(output_csv_name, 'w')
            bcolors.printc(bcolors.OKGREEN, 'write ' + output_csv_name + '...')
            writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))

            writer.writeheader()
            for row in data:
                writer.writerow(row)
            output.close()
            return

        for index in range(data):
            self.write_to_csv(output_name + '_' + str(index), data[index])

    def write(self):
        return self.write_to_csv(self.name, self.data)

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

def tiny_mdb():
    builtin_policys = [
        mdbp_filter_column,
        mdbp_select_charge,
        mdbp_filter_bin,
        mdbp_filter_zero_negative_value,
    ]

    p = MdbPolicy()
    p.register_groups(builtin_policys)

    summary = []
    for mdb in glob.glob(MDB_FOLDER + r'/*.mdb'):
        m = Mdb(mdb, p)
        m.process()
        m.write()
        summary.append(m.summary())

    if len(summary) == 0:
        return

    with open(OUT_SUMMARY, 'w', newline='') as f:
        bcolors.printc(bcolors.OKGREEN, 'write ' + OUT_SUMMARY + '...')
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

if __name__ == '__main__':
    tiny_mdb()
