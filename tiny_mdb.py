import sys
import os
import glob
import shutil
# import pyodbc
from meza import io

MDB_FOLDER = 'mdbs'
OUT_FOLDER = 'outputs'
FORMAT_MDB = 'mdb'
FORMAT_CSV = 'csv'
EXCLUDE_COLUMN = ['Record', 'Classification', 'SerialNumber', 'CellArea', 'Tmonicell', 'Operator', 'Temperature', 'E', 'Pmpp', 'Umpp', 'Impp', 'Jmpp', 'Jsc', 'URev1', 'URev2', 'Ivld1', 'Uvld1', 'Pvld1', 'Ivld2', 'Uvld2', 'Pvld2', 'IRevmax', 'URevmax', 'CellTyp', 'TestTime', 'TestDate']


def output_to_file(f, output):
    rc = []
    # x = 0
    for i in output:
        # if x is 0:
        #     print(i)
        #     x = x + 1
        rc.append(','.join(i))
    return f.write('\n'.join(rc))

def iter_mdb(records):
    try:
        first = next(records)
    except:
        return None
    return first

def parse_mdb(f, mdb):
    data = []
    header = []

    # read mdb file
    records = io.read(mdb)
    line = next(records)

    # store header
    for elem in line:
        if elem in EXCLUDE_COLUMN:
            continue
        header.append(elem)

    # print(header)
    # store data
    charges = set()
    while line != None:
        data_line = []
        for elem in line:
            if elem in EXCLUDE_COLUMN:
                continue
            data_line.append(line[elem])
        data.append(data_line)
        line = iter_mdb(records)

    # sort charge
    list(charges).sort(key=lambda x : len(x))

    for i in charges:
        print(len(i))

    # write header
    f.write(','.join(header) + '\n')
    # write data
    output_to_file(f, data)

def tiny_mdb():
    for mdb in glob.glob(MDB_FOLDER + r'/*.mdb'):
        print('parse ' + mdb + '...')
        f = open(mdb.replace(MDB_FOLDER, OUT_FOLDER).replace(FORMAT_MDB, FORMAT_CSV), 'w')
        parse_mdb(f, mdb)
        f.close()

if __name__ == '__main__':
    tiny_mdb()
