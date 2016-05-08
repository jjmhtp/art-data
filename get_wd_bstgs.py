#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import json

def wd_query(params):
    """Perform a query with Wikidata Query with a given query string"""
    f = urllib.request.urlopen('http://wdq.wmflabs.org/api?' +
                               urllib.parse.urlencode(params))
    f = f.read().decode('utf-8')
    g = json.loads(f)
    return g

def get_wd_bstgs():
    """Get the QIDs and inventory numbers of Wikidata items for BStGS \
    artworks and save them in a JSON file"""
    paramsdict = {'q': '(CLAIM[195:812285] OR CLAIM[195:\
        (CLAIM[361:812285])] OR CLAIM[276:812285] OR CLAIM[276:(CLAIM[361:\
        812285])]) AND CLAIM[217]', 'props': '217'}
    bstgsArtWD =  wd_query(paramsdict)
    items = bstgsArtWD['items']
    for itempos in range(len(items)):
        items[itempos] = {'wdqid': items[itempos], 'invno': []}
        for artwork in bstgsArtWD['props']['217']:
            if items[itempos]['wdqid'] == artwork[0]:
                items[itempos]['invno'].append(artwork[2])
    result = json.dumps(items, ensure_ascii=False, indent=4)
    with open('data/wd_invnos.json', 'w+') as output:
        output.write(result)
    print('Inventory numbers of Wikidata items for BStGS artworks ' +
          'refreshed to data/wd_invnos.json!')

if __name__ == "__main__":
    get_wd_bstgs()


