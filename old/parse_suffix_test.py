

# CAN THIS FILE BE DELETED (saving the test cases)?????????


def count_creators():
    """count number of different creator strings"""
    import csv
    with open('data/bstgs_inventory.csv', 'r') as inventory:
        inventory = csv.reader(inventory)
        i = 0
        creators = []
        creatorslinkedwithund = []
        for line in inventory:
            i += 1
            creators.append(line[1])
            if ' mit ' in line[1]:
                creatorslinkedwithund.append(line[1])
    differentcreators = len(set(creators))
    print('Number of artworks: ', i)
    print('Number of creators: ', differentcreators)
    print(creatorslinkedwithund)


## testing regular expression substitution of creator strings

import re

liste = ['Dürer Albrecht', 'Bosschaert der Ältere Ambrosius', 'Bouts Dieric der Ältere', 'Brueghel der Jüngere Jan', 'Horemans Jan Joseph der Ältere', 'Meer (Vermeer) Jan van der der Ältere',
"Ahlers-Hestermann Friedrich", "Arthois Jacques d'", "Baldung gen. Grien Hans", "Balen Hendrik van mit Jan Brueghel d. Ä.", "Barbari Jacopo de'", "Becher Bernd &. Hilla", "Becher Bernd und Hilla", "Belling Peter ? oder Rudolf ?", "Belotto gen. Canaletto", "Benlliure y Gil José",
"Blanche (Jaques-) Emile", "Boeckhorst Jan mit Peter Paul Rubens (?)", "Bopp(?) Sebald", "Brassai (Gyula Halàsz)", "Brummer (?) oder Brunner A(dolf) (?)", "Brus / Bauer / Nitsch / Rühm", "Buddha (Thailand)", "Burrell Jos(eph?)", "Canlassi (gen. Cagnacci) Guido", "Caravaggio (Michelangelo Merisi) (Kopie nach)",
"Carracci-Schule (Bolognesisch um 1600)", "Cesari (gen. Cavalier d'Arpino) Giuseppe", "Coecke van Aelst Pieter (Replik)", "Cornelisz Jacob (Werkstattkopie)", "d'Arthois Jacques", "de Faye J.", "de Fiori Ernesto", "De Maria Walter", "Guercino (= Barbieri) (Giovanni Francesco)", "Gruppe Virus (Lochmüller Peter)"]
liste2 = liste

for item in liste2:
    print(item)

print('\nPARSED:')


def parse_creator_string(input_string):
    m = re.search(r'\A(?P<lastname>(De |de )?\S*( y \w*| van \w*)?)'
        r'( (?P<suffix1>(der Ältere|der Jüngere)))?'
        r'( (?P<bracket>\()?gen\. (?P<called>(?(bracket)[^()]*|\S*))'
        r'(?(bracket)\)|))?'
        r'( \((?P<inbrackets>[^()]*)\))?'
        r'( (?P<firstname>.*?(?= der Ältere$| der Jüngere$|$)))?'
        r'( (?P<suffix2>(der Ältere$|der Jüngere$|$)))?', input_string)
    # not fixed: 'Blanche (Jaques-) Emile' will not be parsed correctly
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
    called = m.group('called')
    additionalinfo =  m.group('inbrackets')
    return parsed_string, called, additionalinfo


for item in liste2:
    print(parse_creator_string(item))


# agenda
# * still to check '8326', 'WAF 776', '5693' etc.

