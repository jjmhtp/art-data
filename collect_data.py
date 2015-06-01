#!/usr/bin/python
# -*- coding: utf-8 -*-


## This version will be written completely new by replacing
## the linear functioning of the first version by functions!


import urllib
import json
import csv


## Function to perform queries with Wikidata Query

def wd_query(params):
    """perform a query with Wikidata Query with a given query string"""
    paramsstring = urllib.urlencode(params)
    f = urllib.urlopen('http://wdq.wmflabs.org/api?%s' % paramsstring)
    g = json.load(f)
    return g


## Get and convert BStGS artworks in Wikidata

paramsdict = {'q': '(CLAIM[195:812285] OR CLAIM[195:\
    (CLAIM[361:812285])] OR CLAIM[276:812285] OR CLAIM[276:(CLAIM[361:\
    812285])]) AND CLAIM[217]', 'props': '217'}
bstgsArtWD =  wd_query(paramsdict)
items = bstgsArtWD[u'items']
for itempos in range(len(items)):
    items[itempos] = {u'wdqid': items[itempos], u'inv': []}
    for artwork in bstgsArtWD[u'props'][u'217']:
        if items[itempos][u'wdqid'] == artwork[0]:
            items[itempos][u'inv'].append(artwork[2])


## Read and convert data from own observation in own.json

ownfile = open('data/own.json', 'r')
#ownfile = ownfile.read()
ownobj = json.load(ownfile)
ownconverted = []
for room in ownobj[u'rooms'].keys():
    for artworkgroup in ownobj[u'rooms'][room]:
        ownconverted.append({u'inv': artworkgroup, u'location': {u'name': \
                            room, u'date': ownobj[u'date'], u'source': u'own'\
                            }})


## Read data from the BStGS inventory list csv file

reader = csv.reader(open('data/bstgs_inventory.csv'))
inv_list = list(row for row in reader)


## Function to unite collected data

def unite(inv):
    """unite the data of Wikidata, the BStGS inventory list and own \
    obervation for an artworkgroup""" # TODO: for now an artworkgroup
    united_artwork_data = {u'inv': inv}
    for artwork in ownconverted: # own observation
        if inv == artwork[u'inv'] or inv in artwork[u'inv']: # TODO: messy \
            # code because of a messy data model at the moment
            united_artwork_data = artwork
    for item in items: # Wikidata
        if inv == item[u'inv'][0]:
            united_artwork_data[u'wdqid'] = item[u'wdqid']
    for artwork in inv_list: # inventory list
        if inv == artwork[0]:
            united_artwork_data[u'artist'] = artwork[1]
            united_artwork_data[u'title'] = artwork[2]
    return json.dumps(united_artwork_data, indent=4)
#print unite(u'537'), unite(u'688'), unite(u'35'), unite(u'698'), unite(u'38')


## Collect data for the artworks from own.json
# TODO: is this necessary?
unitedlist = []
for artwork in ownconverted:
  try:
    unitedlist.append(unite(artwork[u'inv']))
  except:
    pass

# Convert the collection to QuickStatements format

def artworkjson2qs(artworkjson):
    outputstr = ''
    if artworkjson[u'wdqid'] != None:
        outputstr.append(artworkjson[u'wdqid'])
    else:
        outputstr.append(u'CREATE')
    return outputstr


print json.dumps(ownconverted, indent=4)

print unitedlist
print artworkjson2qs(unitedlist[0])


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




