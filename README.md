```
  _____               _   _     __   __  __  __   ____    ____   
 |_ " _|     ___     | \ |"|    \ \ / /U|' \/ '|u|  _"\U | __")u 
   | |      |_"_|   <|  \| |>    \ V / \| |\/| |/| | | |\|  _ \/ 
  /| |\      | |    U| |\  |u   U_|"|_u | |  | |U| |_| |\| |_) | 
 u |_|U    U/| |\u   |_| \_|      |_|   |_|  |_| |____/ u|____/  
 _// \\_.-,_|___|_,-.||   \\,-.-,//|(_ <<,-,,-.   |||_  _|| \\_  
(__) (__)\_)-' '-(_/ (_")  (_/ \_) (__) (./  \.) (__)_)(__) (__) 
```

# Tiny Mdb
> **Tiny Mdb**, simple tool for mdb data processing.

[![Build Status](https://api.travis-ci.com/OSTnm/tiny_mdb.svg?branch=master)](https://travis-ci.com/OSTnm/tiny_mdb)

Tiny Mdb generate csv based on mdb with builtin policies.

| Platform                       | Test Result |
| ------------------------------ | ----------- |
| Win10 VM                       | ✔           |
| Mac                            | ✔           |

## Usage

- put mdb files to mdbs/
- python tiny_mdb.py or python tiny_mdb.py -p policy.csv
- csv will be generated in outputs

```
usage: tiny_mdb.py [-h] [-p [POLICY]]

Simple tool for mdb data processing.

Supported policy:
.
|-- SPLIT
|   |-- DATE <hours>          split per <hours> hours
|   `-- NUM <number>          split per <number> lines
|-- STR
|   |-- MAX_LEN               string length is longest
|   |-- MIN_LEN               string length is shortest
|   |-- GLOB <glob>           wildcard matching
|   `-- REGEX <regex>         regular expression matching
`-- VAL <condition>           condition matching

Sample:
SPLIT:NUM:500 - split mdb per 500 lines
SPLIT:DATE:2  - split mdb per 2 hours
STR:MIN_LEN   - select longest string for specific key
VAL:>0        - select float value > 0 for specific key

optional arguments:
  -h, --help            show this help message and exit
  -p [POLICY], --policy [POLICY]
                        specify policy file
  -s [SRC], --src [SRC]
                        specify mdb folder
  -d [DST], --dst [DST]
                        specify output folder
```

## Upcoming

-  generate summary dynamically

## Dependency

- mdbtools
- meza

# License

**Tiny Mdb** is released under the terms of Apache License, Version 2.0. Please refer to the LICENSE file.

- - -
