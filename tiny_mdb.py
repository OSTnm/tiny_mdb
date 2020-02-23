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
from argparse import RawTextHelpFormatter
import datetime

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
        self.name = name
        self.uoc_invalid = 0
        self.isc_invalid = 0
        self.rser_invalid = 0
        self.rsh_invalid = 0
        self.ff_invalid = 0
        self.eff_invalid = 0
        self.irev1_invalid = 0
        self.irev2_invalid = 0
        self.bin_invalid = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if len(data) == 0 or type(data[0]) is not dict:
             raise ValueError("invalid data!")
        self._data = data
        return

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
        rc['Number'] = len(self.data)
        for k in keys:
            res = [sub[k] for sub in self.data]
            res = list(map(float, res))
            rc[k] = sum(res) / len(res)
        rc['BIN invalid'] = self.bin_invalid
        rc['Uoc invalid'] = self.uoc_invalid
        rc['Isc invalid'] = self.isc_invalid
        rc['Rser invalid'] = self.rser_invalid
        rc['Rsh invalid'] = self.rsh_invalid
        rc['FF invalid'] = self.ff_invalid
        rc['EFF invalid'] = self.eff_invalid
        rc['IRev1 invalid'] = self.irev1_invalid
        rc['IRev2 invalid'] = self.irev2_invalid
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
    mdb.bin_invalid = count
    mdb.data = rc
    return mdb

@mdbp
def mdbp_filter_invalid_value(mdb):
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
                # TBO, now it is quirk way
                code = 'mdb.{0}_invalid = mdb.{0}_invalid + 1'.format(k.lower())
                exec(code)
                break
        if invalid:
            continue
        rc.append(row)

    mdb.data = rc
    return mdb

@mdbp
def mdbp_split_num_test(mdb):
    data = mdb.data
    n = 500
    mdbs = []

    datas = [data[i:i+n] for i in range(0, len(data), n)]
    for index in range(len(datas)):
        m = Mdb(mdb.name + '_' + str(index), data=datas[index])
        mdbs.append(m)

    return mdbs

@mdbp
def mdbp_split_date_test(mdb):
    data = mdb.data
    mdbs = []

    if len(data) == 0:
        return mdb

    start = 0
    start_time = datetime.datetime.strptime(data[0]['Date'], "%d.%m.%Y-%H:%M:%S")
    offset = 0
    for index in range(1, len(data)):
        now = datetime.datetime.strptime(data[index]['Date'], "%d.%m.%Y-%H:%M:%S")
        diff = (now - start_time).total_seconds()
        if diff < 2 * 60 * 60:
            continue
        sub = data[start:index]
        m = Mdb(mdb.name + '_' + str(offset), data=sub)
        mdbs.append(m)
        offset = offset + 1
        start = index
        start_time = now

    if start < len(data) - 1:
        sub = data[start:]
        m = Mdb(mdb.name + '_' + str(offset), data=sub)
        mdbs.append(m)

    return mdbs

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

def mdbp_func_sanity_check(func, name):
    if func.__name__ != name:
        bcolors.printc(bcolors.FAIL, ' expect ' + name + ' but get ' + func.__name__)
        return False

    if 'mdb' not in func.__code__.co_varnames:
        bcolors.printc(bcolors.FAIL, name + ' parameters not match!')
        return False
    return True

def mdbp_gen_split_num(name, key, limit):
    condition = limit.split(':')[2]
    code = \
'''
@mdbp
def {0}(mdb):
    data = mdb.data
    n = {1}
    mdbs = []

    datas = [data[i:i+n] for i in range(0, len(data), n)]
    for index in range(len(datas)):
        m = Mdb(mdb.name + '_' + str(index), data=datas[index])
        mdbs.append(m)

    return mdbs
'''.format(name, condition)
    exec(code)
    func = locals()[name]
    bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'load policy - ' + name + ' ' + limit)
    return func

def mdbp_gen_split_date(name, key, limit):
    condition = limit.split(':')[2]
    code = \
'''
@mdbp
def {0}(mdb):
    data = mdb.data
    mdbs = []

    if len(data) == 0:
        return mdb

    start = 0
    start_time = datetime.datetime.strptime(data[0]['{1}'], "%d.%m.%Y-%H:%M:%S")
    offset = 0
    for index in range(1, len(data)):
        now = datetime.datetime.strptime(data[index]['{1}'], "%d.%m.%Y-%H:%M:%S")
        diff = (now - start_time).total_seconds()
        if diff < {2} * 60 * 60:
            continue
        sub = data[start:index]
        m = Mdb(mdb.name + '_' + str(offset), data=sub)
        mdbs.append(m)
        offset = offset + 1
        start = index
        start_time = now

    if start < len(data) - 1:
        sub = data[start:]
        m = Mdb(mdb.name + '_' + str(offset), data=sub)
        mdbs.append(m)

    return mdbs
'''.format(name, key, condition)
    exec(code)
    func = locals()[name]
    bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'load policy - ' + name + ' ' + limit + ' hours')
    return func

def mdbp_gen_split(name, key, limit):
    types = {'NUM' : mdbp_gen_split_num, 'DATE': mdbp_gen_split_date}
    return types[limit.split(':')[1]](name, key, limit)

def mdbp_gen_filter_val(name, key, limit):
    condition = limit.split(':')[1]

    code = \
'''
@mdbp
def {0}(mdb):
    keys = ['{1}']
    rc = []
    data = mdb.data

    if len(data) == 0:
        return

    for k in keys:
        if k not in data[0]:
            bcolors.printc(bcolors.FAIL, 'column ' + k + ' not found')
            raise


    count = 0
    for row in data:
        invalid = False
        for k, v in row.items():
            if k not in keys:
                continue
            if not is_float(v) or not (float(v) {2}):
                invalid = True
                break
        if invalid:
            count = count + 1
            continue
        rc.append(row)

    mdb.{3} = count
    mdb.data = rc
    return mdb
'''.format(name, key, condition, key.lower() + '_invalid')
    exec(code)
    func = locals()[name]
    bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'load policy - ' + name + ' ' + limit)
    return func

def mdbp_gen_filter_str(name, key, limit):
    limits = ['MIN_LEN', 'MAX_LEN']
    condition = limit.split(':')[1]

    if condition not in limits:
        raise RuntimeError("invalid policy - str!")
    code = \
    '''
@mdbp
def {0}(mdb):
    rc = []
    data = mdb.data
    str_set = set()
    for row in data:
        if '{1}' not in row:
            bcolors.printc(bcolors.FAIL, 'column {1} not found ')
            raise ValueError("invalid key!")
        str_set.add(row['{1}'])
    str_set = list(str_set)
    str_set.sort(key=lambda x : len(x), reverse={2})
    peak_len = len(str_set[0])
    str_set = [i for i in str_set if len(i) == peak_len]
    bcolors.printc(bcolors.OKGREEN, 'select {1}:')
    for i in str_set:
        bcolors.printc(bcolors.OKBLUE, i)
    for row in data:
        if row['{1}'] not in str_set:
            continue
        rc.append(row)
    mdb.data = rc
    return mdb
    '''.format(name, key, 'False' if 'MIN_LEN' in limit else 'True')
    exec(code)
    func = locals()[name]
    bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'load policy - ' + name + ' ' + limit)
    return func

def mdbp_gen_filter_column(included):
    code = 'INCLUDED_COLUMN = {}'.format(included)
    exec(code)

    bcolors.printc(bcolors.OKGREEN + bcolors.BOLD, 'load policy - mdbp_filter_column')
    if not mdbp_func_sanity_check(mdbp_filter_column, 'mdbp_filter_column'):
        raise RuntimeError("invalid policy!")
    return mdbp_filter_column

def mdbp_get_from_file(name):
    policys = []
    policys_csv = []
    gen_dict = {'STR':mdbp_gen_filter_str, 'VAL': mdbp_gen_filter_val, 'SPLIT': mdbp_gen_split}
    name_dict = {'STR':'mdbp_filter_str', 'VAL':'mdbp_filter_val', 'SPLIT':'mdbp_split'}

    with open(name, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            policys_csv.append(row)

    if 0 == len(policys_csv):
        raise RuntimeError("invalid policy!")

    # gen column filter at first
    filter_column = mdbp_gen_filter_column(list(policys_csv[0].keys()))
    policys.append(filter_column)

    # gen policy based on type
    for index in range(len(policys_csv)):
        suffix = '_row' + str(index) + '_'
        for k, v in policys_csv[index].items():
            if v.strip() == '':
                continue
            gen_type = v.split(':')[0]
            if gen_type not in name_dict:
                raise RuntimeError("unkown policy! " + v)
            func_name = name_dict[gen_type] + suffix + k
            gen_fun = gen_dict[gen_type](func_name, k, v)
            if not mdbp_func_sanity_check(gen_fun, func_name):
                raise RuntimeError("invalid policy!")
            policys.append(gen_fun)

    return policys

def tiny_mdb(args):
    builtin_policys = [
        mdbp_filter_column,
        mdbp_select_charge,
        mdbp_filter_bin,
        mdbp_filter_invalid_value,
        # mdbp_split_date_test,
        # mdbp_split_num_test,
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

welcome_msg = \
r'''
 _   _                           _ _
| | (_)                         | | |
| |_ _ _ __  _   _ _ __ ___   __| | |__
| __| | '_ \| | | | '_ ` _ \ / _` | '_ \
| |_| | | | | |_| | | | | | | (_| | |_) |
 \__|_|_| |_|\__, |_| |_| |_|\__,_|_.__/
              __/ |
             |___/
'''

desc = \
'''
Simple tool for mdb data processing.

Supported policy:
.
|-- SPLIT
|   |-- DATE <hours> split per <hours> hours
|   `-- NUM <number> split per <number> lines
|-- STR
|   |-- MAX_LEN      hit if string length is longest
|   `-- MIN_LEN      hit if string length is shortest
`-- VAL <condition>  hit if condition is True

Sample:
SPLIT:NUM:500 - split mdb per 500 lines
SPLIT:DATE:2  - split mdb per 2 hours
STR:MIN_LEN   - select longest string for specific key
VAL:>0        - select float value > 0 for specific key
'''

def cli_init():
    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p', '--policy', nargs='?', help='specify policy file')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    bcolors.printc(bcolors.BOLD, welcome_msg)
    args = cli_init()
    tiny_mdb(args)
