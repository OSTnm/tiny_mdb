```bash
 _   _                           _ _
| | (_)                         | | |
| |_ _ _ __  _   _ _ __ ___   __| | |__
| __| | '_ \| | | | '_ ` _ \ / _` | '_ \
| |_| | | | | |_| | | | | | | (_| | |_) |
 \__|_|_| |_|\__, |_| |_| |_|\__,_|_.__/
              __/ |
             |___/
```

# Tiny Mdb
> **Tiny Mdb**, simple tool for mdb data processing.

Tiny Mdb generate csv based on mdb with builtin policies.

| Platform                       | Test Result |
| ------------------------------ | ----------- |
| Win10 VM                       | ✔           |
| Mac                            | ✔           |

## Usage

- put mdb files to mdbs/
- python tiny_mdb.py or python tiny_mdb.py -p policy.csv
- csv will be generated in outputs

```bash
usage: tiny_mdb.py [-h] [-p [POLICY]]

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

optional arguments:
  -h, --help            show this help message and exit
  -p [POLICY], --policy [POLICY]
                        specify policy file
```

## Upcoming

-  generate summary dynamically

## Dependency

- mdbtools
- meza

# License

**Tiny Mdb** is released under the terms of Apache License, Version 2.0. Please refer to the LICENSE file.

- - -
