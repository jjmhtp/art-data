#!/usr/bin/python
# -*- coding: utf-8 -*-


## This script does not work so far :-/
## This version 2 will be written almost completely from scratch by replacing
## the linear functioning of the first version by functions!

import urllib
import json
import ast

## Get artworks yet in Wikidata

def wd_query(params):
    """perform a query with Wikidata Query with a given query string"""
    paramsstring = urllib.urlencode(params)
    f = urllib.urlopen('http://wdq.wmflabs.org/api?%s' % paramsstring)
    g = json.load(f)
    return g

#TODO: arrange entities with more than one inventory number: complex JSONs
#      should be created
paramsdict = {'q': '(CLAIM[195:812285] OR CLAIM[195:\
    (CLAIM[361:812285])] OR CLAIM[276:812285] OR CLAIM[276:(CLAIM[361:\
    812285])]) AND CLAIM[217]', 'props': '217'}
bstgsArtWD =  wd_query(paramsdict)


bstgsArtWDjson = bstgsArtWD[u'items']
print bstgsArtWDjson



#h = open('mkTable4qStatementsOutput.txt', 'w')
#h.write(str(g))
#h.close()
#
#i = open('mkTable4qStatementsOutput.txt', 'r')
#j = i.read()
#print 'file:', j
#i.close()




#k = open('mkTable4qStatementsOutput.txt', 'r')
#l = k.read()
#k.close()
#m = ast.literal_eval(l)


## Get artworks to extend

#inputart1 = open('rooms.json', 'r')
#inputart2 = json.load(inputart1)
#inputart1.close()
#
#for room in inputart2[u'rooms']:
#    for item in inputart2[u'rooms'][room]:
#        if type(item) != list:
#            inputart2[u'rooms'][room][inputart2[u'rooms'][room].index(item)] = [item]
##print inputart2
#
#artworkslist = []
#for room in inputart2[u'rooms']:
#    for item in inputart2[u'rooms'][room]:
#        artworkslist.append({'group': item, 'roomstatement': {'room': room, 'date': inputart2[u'date']}})


## Enrich artworks to extend

### Enrich artworks to extend from inventory list

#import csv
#reader = csv.reader(open('inv4.csv'))
#inv_list = list(row for row in reader)
#
#for row in inv_list:
#    for group in artworkslist:
#        for invitem in artworkslist[artworkslist.index(group)]['group']:
#            if row[0] == invitem:
#                artworkslist[artworkslist.index(group)]['group'][artworkslist[artworkslist.index(group)]['group'].index(invitem)] = {'Inv. No.': invitem, 'artist': row[1], 'title': row[2]} 
#
#print artworkslist

#### Get possible Wikidata matches for the artist TODO: not yet adapted

#nameparts = artworkslist[0]['artist'].split(' ', 1)
#queryname = '+'.join((nameparts[1],nameparts[0]))
#queryname.replace(' ','+')
#params = urllib.urlencode({'action': 'wbsearchentities', 'language': 'de', 'format': 'json'})
#f = urllib.urlopen('http://www.wikidata.org/w/api.php?search=%(queryname)s&%(params)s' % {'queryname': queryname, 'params': params})
#g = json.load(f)
#artworkslist[0]['possible artists'] = g[u'search']

### Enrich artworks to extend with Wikidata QIDs TODO: not yet adapted

#for item in m[u'props'][u'217']:
#    if item[2] == artworkslist[0]['Inv. No.']:
#        artworkslist[0]['WD ID'] = item[0]
#print artworkslist



# agenda
# * make functions out of the linear code!!!
# * all list-iterations have to be improved with simple counts somewhat like: for a in range(0,len(listname)




