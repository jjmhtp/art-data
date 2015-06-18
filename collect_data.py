#!/usr/bin/env python3
# -*- coding: utf-8 -*-


## This version will be written completely new by replacing
## the linear functioning of the first version by functions!


#import urllib.request, urllib.parse, urllib.error
import json
import csv
import sys

inputinvno = sys.argv[1]


wdinvnosfile = open('data/wd_invnos.json', 'r')
items = json.load(wdinvnosfile)


## Read data from the BStGS inventory list csv file

reader = csv.reader(open('data/bstgs_inventory.csv'))
inv_list = list(row for row in reader)






## Function to unite collected data

def unite(inv):
    """unite the data of Wikidata, the BStGS inventory list and own \
    obervation for an artworkgroup""" # TODO: for now an artworkgroup
    united_artwork_data = {'inv': inv}
    for item in items: # Wikidata
        if inv in item['inv']:
            united_artwork_data['wdqid'] = item['wdqid']
    for artwork in inv_list: # inventory list
        if inv == artwork[0]:
            united_artwork_data['artist'] = artwork[1]
            united_artwork_data['title'] = artwork[2]
    return united_artwork_data


# Convert the collection to QuickStatements format

def artworkjson2qs(artworkjson):
    outputstr = ''
    if 'wdqid' in artworkjson:
        ref = ('Q' + str(artworkjson['wdqid']))
    else:
        outputstr += 'CREATE\n'
        ref = 'LAST'
    outputstr += (ref + '	Lde	"' + artworkjson['title'] + '"\n')
    outputstr += (ref + '	P170	[' + artworkjson['artist'] + ']\n')
    outputstr += (ref + '	P217	"' + artworkjson['inv'] + '"	P195	Q812285\n')
    return outputstr


#print(json.dumps(ownconverted, indent=4))


#print unite(u'537'), unite(u'688'), unite(u'35'), unite(u'698'), unite(u'38')

print(json.dumps(unite(inputinvno), indent=4))
print(artworkjson2qs(unite(inputinvno)))


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




