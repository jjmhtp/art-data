#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import csv
import json


def parse_creator_rest(input_string):
# TODO: move this functionality to the artworkjson2qs function not to write
#       its results to the json file: take the 'import re', too!
    m = re.search(r'\A(?P<lastname>(De |de )?\S*( y \w*| van \w*)?)'
        r'( (?P<suffix1>(der Ältere|der Jüngere)))?'
        r'(,? (?P<bracket>\()?genannt (?P<called>(?(bracket)[^()]*|\S*))'
        r'(?(bracket)\)|))?' # FIXME: correct?
        r'( \((?P<inbrackets>[^()]*)\))?'
        r'( (?P<firstname>.*?(?= der Ältere$| der Jüngere$|$)))?'
        r'( (?P<suffix2>(der Ältere$|der Jüngere$|$)))?'
        r'( (?P<bracket2>\()?genannt (?P<called2>(?(bracket2)[^()]*|\S*))'
        r'(?(bracket2)\)|))?', # FIXME: correct?
        input_string)
    # not fixed: 'Blanche (Jaques-) Emile' will not be parsed correctly
    # TODO: issues with 'gen.'/'genannt' and with 'Stott'
    parsed_string = ''
    if m.group('firstname'):
        parsed_string += m.group('firstname')
    if m.group('lastname'):
        if m.group ('firstname') and parsed_string[-3:] != " d'":
            parsed_string += ' '
        parsed_string += m.group('lastname')
    if m.group('suffix1'):
        parsed_string += ' ' + m.group('suffix1')
    if m.group('suffix2'):
        parsed_string += ' ' + m.group('suffix2')
    for string in [' und ', ' mit ', ' &. ', ' oder ', ' / ', 'Gruppe ']:
        if string in input_string:
            parsed_string = input_string
    called = ''
    if m.group('called'):
        called += m.group('called')
    if m.group('called2'):
        called += m.group('called2')
    # 'called' and 'called2' should be mutually exclusive
    additionalinfo =  m.group('inbrackets')
    return parsed_string, called, additionalinfo

def parse_creator(creator_string):
    # Extract indications of the relation of the creator to the person named
    # and remove them
    creator_string_suffixes = [
        '(Art des)', '(Kopie nach)', '(Nach)',
        '(Nachahmer)', '(Nachfolger)', '(Schule)', '(Umkreis)',
        '(vermutlich)', '(Werkstatt)', '(zugeschrieben)', '(?)',
        '(Anonymer Meister seiner Werkstatt)', '(Werkstatt?)', '(Replik)',
        '(Werkstattkopie)'
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
    creator_string = creator_string.replace('gen.', 'genannt')
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
        creator_string, called, additionalinfo = parse_creator_rest(
            creator_string)
    # Set the value field and the qualifiers field if there was an additional
    # indication to the person named
    creator_dict = {'value': creator_string}
    if 'called' in locals() and called:
        creator_dict['called'] = called
    if 'additionalinfo' in locals() and additionalinfo:
        creator_dict['additionalinfo'] = additionalinfo
    # TODO: these information should normally go one step deeper into
    # the qualifiers
    if qualifier: # overwrite eventually
        creator_dict['value'] = 'Unbekannt'
        creator_dict['qualifiers'] = {qualifier: creator_string}
    return creator_dict

def convert_row(row):
    dictionary = {}
    # Compose dictionaries for the rows from the fields of the csv file
    # FIXME: Sometimes the fields do not come stripped, so they are here.
    dictionary['invno'] = row[0].strip()
    dictionary['creator'] = parse_creator(row[1].strip())
    title_string = row[2].replace(', gen.', ', genannt')
    dictionary['title'] = title_string.strip()
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


