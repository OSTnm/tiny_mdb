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
INCLUDED_COLUMN = ['Record', 'Charge', 'Date', 'BIN', 'Uoc', 'Isc', 'Rser', 'Rsh', 'FF', 'EFF', 'IRev1', 'IRev2']


def output_to_file(f, output):
    rc = []
    # x = 0
    for i in output:
        # if x is 0:
        #     print(i)
        #     x = x + 1
        rc.append(','.join(map(str, i)))
    return f.write('\n'.join(rc))

def iter_mdb(records):
    try:
        first = next(records)
    except:
        return None
    return first

def parse_mdb(out_raw, out_summary, mdb):
    raw_data = []
    header = []

    # read mdb file
    # mdb = mdb.encode('utf-8')
    records = io.read(mdb)
    line = next(records)

    # store header
    for elem in line:
        if elem not in INCLUDED_COLUMN:
            continue
        header.append(elem)

    # print(header)
    # store data
    charges = set()
    while line != None:
        data_line = []
        for elem in line:
            if elem not in INCLUDED_COLUMN:
                continue
            charges.add(line['Charge'])
            data_line.append(line[elem])
        raw_data.append(data_line)
        line = iter_mdb(records)

    # sort charge
    charges = list(charges)
    charges.sort(key=lambda x : len(x))
    charges_len = len(charges[0])
    for i in range(1, len(charges)):
        if len(charges[i]) != charges_len:
            charges = charges[:i]
            break
    print('select charges:')
    for i in charges:
        print(i + '   length: ' + str(len(i)))

    # filter charge
    charge_index = header.index('Charge')
    data = []
    for line in raw_data:
        if not line[charge_index] in charges:
            continue
        data.append(line)

    # filter BIN = 23 24
    BIN_invalid_count = 0
    BIN_index = header.index('BIN')
    data2 = []
    for line in data:
        if 22 < int(float(line[BIN_index])):
            BIN_invalid_count = BIN_invalid_count + 1
            continue
        data2.append(line)
    print('BIN invalid: ' + str(BIN_invalid_count))

    # remove Charge Date BIN
    data3 = []
    data4 = []
    for line in data2:
        temp = line
        line = line[4:]

        invalid = False
        for elem in line:
            if len(elem.strip()) == 0:
                invalid = True
                break
            if float(elem) < 0:
                invalid = True
                break
        if invalid:
            print('Warning: ' + str(temp) + ', Ignore!')
            continue
        temp = temp[:4]
        temp.extend(list(map(float, line)))
        data3.append(temp)
        data4.append(list(map(float, line)))

    summary = list(map(lambda x: sum(x)/len(x), zip(*data4)))

    # write raw
    # write header
    out_raw.write(','.join(header) + '\n')
    # write data
    output_to_file(out_raw, data3)

    # write summary
    # write summary header
    header = header[4:]
    header.extend(['BIN invalid', 'Num'])
    out_summary.write(','.join(header) + '\n')
    # write average data
    summary.extend([BIN_invalid_count, len(data4)])
    out_summary.write(','.join(map(str, summary)) + '\n')

def tiny_mdb():
    for mdb in glob.glob(MDB_FOLDER + r'/*.mdb'):
        print('parse ' + mdb + '...')

        out_raw = mdb.replace(MDB_FOLDER, OUT_FOLDER).replace(FORMAT_MDB, FORMAT_CSV)
        out_summary = out_raw + '_summary.csv'
        out_raw = open(out_raw, 'w')
        out_summary = open(out_summary, 'w')
        parse_mdb(out_raw, out_summary, mdb)
        out_raw.close()
        out_summary.close()

if __name__ == '__main__':
    tiny_mdb()
