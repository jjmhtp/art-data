
def count_creators():
    """count number of different creator strings"""
    import csv
    with open('data/bstgs_inventory.csv', 'r') as inventory:
        inventory = csv.reader(inventory)
        i = 0
        creators = []
        for line in inventory:
            i += 1
            creators.append(line[1])
    differentcreators = len(set(creators))
    print('Number of artworks: ', i)
    print('Number of creators: ', differentcreators)


## testing regular expression substitution of creator strings

import re

liste = ['Dürer Albrecht', 'Bosschaert der Ältere Ambrosius', 'Bouts Dieric der Ältere', 'Brueghel der Jüngere Jan', 'Horemans Jan Joseph der Ältere', 'Meer (Vermeer) Jan van der der Ältere',
"Ahlers-Hestermann Friedrich", "Arthois Jacques d'", "Baldung gen. Grien Hans", "Balen Hendrik van mit Jan Brueghel d. Ä.", "Barbari Jacopo de'", "Becher Bernd &. Hilla", "Becher Bernd und Hilla", "Belling Peter ? oder Rudolf ?", "Belotto gen. Canaletto", "Benlliure y Gil José",
"Blanche (Jaques-) Emile", "Boeckhorst Jan mit Peter Paul Rubens (?)", "Bopp(?) Sebald", "Brassai (Gyula Halàsz)", "Brummer (?) oder Brunner A(dolf) (?)", "Brus / Bauer / Nitsch / Rühm", "Buddha (Thailand)", "Burrell Jos(eph?)", "Canlassi (gen. Cagnacci) Guido", "Caravaggio (Michelangelo Merisi) (Kopie nach)",
"Carracci-Schule (Bolognesisch um 1600)", "Cesari (gen. Cavalier d'Arpino) Giuseppe", "Coecke van Aelst Pieter (Replik)", "Cornelisz Jacob (Werkstattkopie)", "d'Arthois Jacques", "de Faye J.", "de Fiori Ernesto", "De Maria Walter", "Guercino (= Barbieri) (Giovanni Francesco)", "Gruppe Virus (Lochmüller Peter)"]
liste2 = liste[0:7]

for item in liste2:
    print(item)

print('\nPARSED:')

for item in liste2:

#    item = re.sub(r'\A(?P<lastname_and_suffix>\w* (der Ältere|der Jüngere)) (?P<rest>.*)', r'\g<rest> \g<lastname_and_suffix>', item)

#    item = re.sub(r'\A(?P<last>\w+( \([\w ]+\))?( der Ältere| der Jüngere)?)(?P<rest>[\w ]*)(?P<suffix>( der Ältere| der Jüngere)?)', r'rest{\g<rest>} last{\g<last>} suffix{\g<suffix>}   [CHANGED]', item)


#    item = re.sub(r'\A(?P<lastname>[\w]*) (?P<firstname>[\w* ]+?) (?P<suffix>(der Ältere|der Jüngere))', r'\g<firstname> \g<lastname> \g<suffix>', item)

    if 0: re.sub(r' \((?P<inbrackets>\w+)\).*', r'\g<0>; inbrackets:\g<1>', liste[-1])


#goal:    item = re.sub(r'''\A(?P<lastname>[\w\-']*)( \((?P<inbrackets>[^()]*)\))?( (?P<firstname>.*(?!der Ältere$|der Jüngere$)))?( (?P<suffix>(der Ältere$|der Jüngere$)))?''', r'\g<firstname> \<lastname> \g<suffix>; inbrackets: \g<inbrackets>', item)
    item2 = re.sub(r'''\A(?P<lastname>[\w\-']*)( \((?P<inbrackets>[^()]*)\))?( (?P<firstname>.*(?!der Ältere$|der Jüngere$)))?(?P<suffix>( der Ältere$| der Jüngere$|$))?''', r'\g<firstname> \g<lastname> \g<suffix>; inbrackets: ', item) # reducing for debugging

    m = re.search(r'''\A(?P<lastname>\S*)( (?P<suffix1>(der Ältere|der Jüngere)))?( \((?P<inbrackets>[^()]*)\))?( (?P<firstname>.*?(?= der Ältere$| der Jüngere$|$)))?( (?P<suffix2>(der Ältere$|der Jüngere$|$)))?''', item)
    # r'\(.*\).*?(?=( der Ältere$|$))'
    result = '"'
    if m.group('firstname'):
        result += m.group('firstname')
    if m.group('lastname'):
        result += ' ' + m.group('lastname')
    if m.group('suffix1'):
        result += ' ' + m.group('suffix1')
    if m.group('suffix2'):
        result += ' ' + m.group('suffix2')
    if m.group('inbrackets'):
        result += ' (' + m.group('inbrackets') + ')'
    result += '"'
#    for part in ['firstname', 'lastname', 'suffix1', 'suffix2', 'inbrackets']:
#        if m.group(part):
#            result += ' ' +  m.group(part)
# str(m.group('firstname')) + ' ' + str(m.group('lastname')) + ' ' + str(m.group('suffix1')) + ' ' + str(m.group('suffix2')) + ' (' + str(m.group('inbrackets')) + ')'



    print(result)


# agenda
# * mind "-"
# * fix "14258	Christo (eigentl. Javacheff		Christo), Valley Curtain !!!!!!!!!!!!!!" elsewhere

