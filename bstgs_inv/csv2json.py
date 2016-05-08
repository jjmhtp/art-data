#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json

parser = argparse.ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('-o', '--outputfile')
args = parser.parse_args()

inputfile = args.inputfile
outputfile = inputfile.rsplit('.csv')[0]+'.json'
if args.outputfile:
    outputfile = args.outputfile

# read csv input file
f = open(inputfile, 'r')
reader = csv.DictReader(f)
dictionarylist = [row for row in reader]

# remove keys with empty strings
for key in reader.fieldnames:
    for dictionary in dictionarylist:
        if dictionary[key] == '':
            del dictionary[key]

# parse as json
output = json.dumps(dictionarylist, ensure_ascii=False, indent=4)
f.close()

# write json output file
try:
    with open(outputfile, 'x') as f:
        f.write(output)
except FileExistsError:
    answer = input('The file "' + outputfile +
                   '"exists yet. Press "y" if you want to overwrite it! ')
    if answer == 'y':
        with open(outputfile, 'w+') as f:
            f.write(output)

