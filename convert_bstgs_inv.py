#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import json

def creator_parse(creator_string):
    # Extract indications of the relation of the creator to the person named
    # and remove them
    creator_string_suffixes = [
        '(Art des)', '(Kopie nach)', '(Nach)',
        '(Nachahmer)', '(Nachfolger)', '(Schule)', '(Umkreis)',
        '(vermutlich)', '(Werkstatt)', '(zugeschrieben)', '(?)',
        '(Anonymer Meister seiner Werkstatt)'
        ]
    qualifier = u''
    for suffix in creator_string_suffixes:
        parts = creator_string.partition(suffix)
        qualifier = qualifier + parts[1].strip('()')
        creator_string = parts[0].strip() + parts[2]
    # Reverse the reversion of first and last names
    if 'Meister' in creator_string or creator_string.startswith((
            'Alpenländisch', 'Augsburgisch', 'Bambergisch', 'Bayerisch',
            'Bolognesisch', 'Byzantinisch-Russisch', 'Chinesisch', 'Deutsch',
            'Donauländisch', 'Englisch', 'Ferraresisch', 'Flämisch',
            'Florentinisch', 'Fränkisch', 'Französisch', 'Genuesisch',
            'Holländisch', 'Indisch', 'Italienisch', 'Japanisch',
            'Katalanisch', 'Kölnisch', 'Lombardisch', 'Mailändisch',
            'Mainfränkischer', 'Mitteldeutsch', 'Mittelrheinischer',
            'Neapolitanisch', 'Niederdeutsch', 'Niederländisch',
            'Niederrheinisch', 'Nordwestdeutsch', 'Nürnbergisch',
            'Oberdeutsch', 'Oberitalienisch', 'Oberrheinisch',
            'Oberschwäbisch', 'Ostbayerisch', 'Österreichisch', 'Römische',
            'Russisch', 'Sardinisch', 'Schwäbisch', 'Seeschwäbisch',
            'Sevillanische', 'Spanisch', 'Süddeutsch',
            'Südtirolisch-Trientinisch', 'Türkische', 'Umbrisch',
            'Venezianisch', 'Veronesisch', 'Vlämisch', 'Westfälisch'
            )):
        pass
    else:
        string_parts = creator_string.split(None, 1)
        string_parts.reverse()
        creator_string = ' '.join(part for part in string_parts)
        # transfer the first word if there are more to the end of the string
    # Set the value field and the qualifiers field if there was an additional
    # indication to the person named
    creator_dict = {u'value': creator_string}
    if qualifier: # overwrite eventually
        creator_dict[u'value'] = u'anonymous'
        creator_dict[u'qualifiers'] = {qualifier: creator_string}
    return creator_dict

def convert_row(row):
    dict = {}
    # Compose dictionaries for the rows from the fields of the csv file
    # (The fields are stripped because some are not yet unfortunately.)
    dict[u'inv'] = row[0].strip()
    dict[u'creator'] = creator_parse(row[1].strip())
    dict[u'title'] = row[2].strip()
    return dict

def iterate_bstgs_inv():
    reader = csv.reader(open('data/bstgs_inventory.csv')) # TODO: unicode issue
    inv_list = list(row for row in reader)
    inv_converted = []
    for row in inv_list:
        inv_converted.append(convert_row(row))
    return inv_converted

print json.dumps(iterate_bstgs_inv()[0:10], indent=4)


# P1877: after a work by
# P1773: attributed to
# Q4233718: anonymous

