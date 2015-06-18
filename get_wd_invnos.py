#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import json

## Function to perform queries with Wikidata Query

def wd_query(params):
    """perform a query with Wikidata Query with a given query string"""
    paramsstring = urllib.parse.urlencode(params)
    f = urllib.request.urlopen('http://wdq.wmflabs.org/api?%s' % paramsstring)
    f = f.read().decode('utf-8')
    g = json.loads(f)
    return g


## Get and convert BStGS artworks in Wikidata

paramsdict = {'q': '(CLAIM[195:812285] OR CLAIM[195:\
    (CLAIM[361:812285])] OR CLAIM[276:812285] OR CLAIM[276:(CLAIM[361:\
    812285])]) AND CLAIM[217]', 'props': '217'}
bstgsArtWD =  wd_query(paramsdict)
items = bstgsArtWD['items']
for itempos in range(len(items)):
    items[itempos] = {'wdqid': items[itempos], 'inv': []}
    for artwork in bstgsArtWD['props']['217']:
        if items[itempos]['wdqid'] == artwork[0]:
            items[itempos]['inv'].append(artwork[2])


result = json.dumps(items, ensure_ascii=False, indent=4)
with open('data/wd_invnos.json', 'w') as output:
    output.write(result)



