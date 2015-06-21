#!/usr/bin/env python3
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
        '(Anonymer Meister seiner Werkstatt)', '(Werkstatt?)'
        ]
    qualifier = ''
    for suffix in creator_string_suffixes:
        parts = creator_string.partition(suffix)
        qualifier = qualifier + parts[1].strip('()')
        creator_string = parts[0].strip() + parts[2]
    # Expand abbreviations for the elder and the younger
    creator_string = creator_string.replace('d.Ä.', 'der Ältere')
    creator_string = creator_string.replace('d. A.', 'der Ältere')
    creator_string = creator_string.replace('d.J.', 'der Jüngere')
    creator_string = creator_string.replace('d. J.', 'der Jüngere')
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
        # TODO: issues with 'd.Ä.' and brackets
        string_parts.reverse()
        creator_string = ' '.join(part for part in string_parts)
        # transfer the first word if there are more to the end of the string
    # Set the value field and the qualifiers field if there was an additional
    # indication to the person named
    creator_dict = {'value': creator_string}
    if qualifier: # overwrite eventually
        creator_dict['value'] = 'Unbekannt'
        creator_dict['qualifiers'] = {qualifier: creator_string}
    return creator_dict

def convert_row(row):
    dictionary = {}
    # Compose dictionaries for the rows from the fields of the csv file
    # (The fields are stripped because some are not yet unfortunately.)
    dictionary['invno'] = row[0].strip()
    dictionary['creator'] = creator_parse(row[1].strip())
    dictionary['title'] = row[2].strip()
    return dictionary

def iterate_bstgs_inv():
    reader = csv.reader(open('data/bstgs_inventory.csv'))
    inv_list = list(row for row in reader)
    inv_converted = []
    for row in inv_list:
        inv_converted.append(convert_row(row))
    return inv_converted

result = json.dumps(iterate_bstgs_inv(), ensure_ascii=False, indent=4)
with open('data/bstgs_inventory.json', 'w+') as output:
    output.write(result)

#print(json.dumps(iterate_bstgs_inv()[0:10], ensure_ascii=False, indent=4))


