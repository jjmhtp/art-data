#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request, urllib.parse, urllib.error
import argparse


## Read data from the BStGS inventory list and the Wikidata list of
## inventory numbers json files
items = json.load(open('data/wd_invnos.json', 'r'))
bstgsinventory = json.load(open('data/bstgs_inventory.json', 'r'))


## Function to unite collected data
def unite(inputdict):
    """unite the data of Wikidata, the BStGS inventory list and given \
    data for an artworkgroup""" # TODO: for now an artworkgroup(?)
    united_artwork_data = inputdict
    for item in items: # Wikidata
        if inputdict['invno'] in item['invno']: # TODO: matches also groups atm
            united_artwork_data['wdqid'] = ('Q' + str(item['wdqid']))
    for artwork in bstgsinventory: # inventory list
        if inputdict['invno'] == artwork['invno']:
            united_artwork_data['creator'] = artwork['creator']
            united_artwork_data['title'] = artwork['title']
    return united_artwork_data


## Search for a creator on Wikidata based on a given string
def search_wd_entities(searchstr, language):
    searchstr.replace(' ','+')
    params = urllib.parse.urlencode({'search': searchstr,
                                     'action': 'wbsearchentities',
                                     'language': language, 'format': 'json'})
    f = urllib.request.urlopen('http://www.wikidata.org/w/api.php?%s' % params)
    f = f.read().decode('utf-8')
    g = json.loads(f)
    possiblematches = g['search']
    # construct a question if one of the possible matches is correct
    question = ('The search for "' + searchstr +
                '" has found ' + str(len(possiblematches)) +
                ' possible matches:\n')
    for i in range(len(possiblematches)):
        label = possiblematches[i].get('label')
        description = possiblematches[i].get('description')
        if label:
            label = '"' + label + '"'
        else:
            label = '[no label]'
        if description:
            description = '"' + description + '"'
        else:
            description = '[no description]'
        question += (str(i+1) + ' ' + label + ' – ' + description +
                     ' (' + possiblematches[i]['id'] + ')\n')
    question += ('Press the number of the correct item or abort with ' +
                 'anything else! ')
    return question, possiblematches


## Try to match a given search string to a Wikidata item with manual checking
def try_matching_str_to_wd(searchstr, language, mappingjsonfile):
    mapping = {}
    try:
        with open(mappingjsonfile, 'r') as readfile:
            mapping = json.load(readfile)
    except (FileNotFoundError, ValueError):
        pass
    if searchstr in mapping:
        response = mapping[searchstr]
    else:
        question, possiblematches = search_wd_entities(searchstr, language)
        # TODO: Make input of alternative search string and result possible!
        try:
            i = int(input(question)) - 1
            if i < 0:
                raise IndexError('Indices < 0 not allowed here!')
            matchedid = possiblematches[i]['id']
            # write newly matched ID to mapping file
            mapping[searchstr] = matchedid
            with open(mappingjsonfile, 'w+') as writefile:
                writefile.write(json.dumps(mapping, ensure_ascii=False,
                                           indent=4, sort_keys=True))
            response = matchedid
        except (ValueError, IndexError):
            response = '[' + searchstr + ']'
    return response


## Convert the collection to QuickStatements format
def artworkjson2qs(artworkjson):
    outputstr = ''
    if 'wdqid' in artworkjson:
        ref = artworkjson['wdqid']
    else:
        outputstr += 'CREATE\n'
        ref = 'LAST'
    # Match creation data to Wikidata
    if 'creator' in artworkjson:
        creator = artworkjson['creator']['value']
        creator = try_matching_str_to_wd(creator, 'de',
            'data/bstgs_wd_creator_mapping.json')
        if 'qualifiers' in artworkjson['creator']:
            creatorqualifierdict = {'Kopie nach': 'P1877',
                                    'zugeschrieben': 'P1773'}
            for key in creatorqualifierdict:
                if key in artworkjson['creator'].get('qualifiers'):
                    #TODO: output the string in () if it could not be mapped
                    creatorinqualifier = artworkjson['creator']['qualifiers']\
                                         [key]
                    creatorinqualifier = try_matching_str_to_wd(
                        creatorinqualifier, 'de',
                        'data/bstgs_wd_creator_mapping.json')
                    creator += ('	' + creatorqualifierdict[key] +
                                '	' + creatorinqualifier)
    # Adding of statement constructors
    if 'title' in artworkjson:
        outputstr += (ref + '	Lde	"' + artworkjson['title'] + '"\n')
    if 'creator' in artworkjson:
        outputstr += (ref + '	P170	' + creator + '\n')
    outputstr += (ref + '	P217	"' + artworkjson['invno'] +
                  '"	P195	Q812285\n')
    if 'image' in artworkjson:
        outputstr += (ref + '	P18	"' + artworkjson['image'] + '"\n')
    if 'commonscat' in artworkjson:
        outputstr += (ref + '	P373	"' + artworkjson['commonscat'] + '"\n')
    if 'depicts' in artworkjson:
        outputstr += (ref + '	P180	"' + artworkjson['depicts'] + '"\n')
    #TODO: non-unique properties such as P180 should be able to have >1 value
    return outputstr


## Try to write a file and ask to overwrite it if it yet exists
def try_write_file(outputfile, output):
    try:
        with open(outputfile, 'x') as f:
            f.write(output)
    except FileExistsError:
        answer = input('The file "' + outputfile +
                       '"exists yet. Press "y" if you want to overwrite it! ')
        if answer == 'y':
            with open(outputfile, 'w+') as f:
                f.write(output)

parser = argparse.ArgumentParser()
parser.add_argument('--invno')
parser.add_argument('--json')
parser.add_argument('-i', '--inputjsonfile')
parser.add_argument('-oaug', '--outputfileaugmented')
parser.add_argument('-oqs', '--outputfilequickstatements')
args = parser.parse_args()

inputinvno = args.invno
if inputinvno:
    inputdict = {'invno': inputinvno}
    uniteddict = unite(inputdict)
    print(json.dumps(uniteddict, ensure_ascii=False, indent=4))
    print(artworkjson2qs(uniteddict))

inputjson = args.json
if inputjson:
    inputdict = json.loads(inputjson)
    uniteddict = unite(inputdict)
    print(json.dumps(uniteddict, ensure_ascii=False, indent=4))
    print(artworkjson2qs(uniteddict))

inputjsonfile = args.inputjsonfile
if inputjsonfile:
    inputdictlist = json.load(open(inputjsonfile, 'r'))
    outputdictlist = []
    outputqs = ''
    for inputdict in inputdictlist:
        uniteddict = unite(inputdict)
        outputdictlist.append(uniteddict)
        outputqs += artworkjson2qs(uniteddict)
    # determine augmented json output file
    outputfileaugmented = inputjsonfile.rsplit('.json')[0]+'_augmented.json'
    if args.outputfileaugmented:
        outputfileaugmented = args.outputfileaugmented
    # determine QuickStatements output file
    outputfileqs = inputjsonfile.rsplit('.json')[0]+'_qs.txt'
    if args.outputfilequickstatements:
        outputfileqs = args.outputfilequickstatements
    # write files
    try_write_file(outputfileaugmented,
                   json.dumps(outputdictlist, ensure_ascii=False, indent=4))
    try_write_file(outputfileqs, outputqs)


#testjson = {"depicts": "", "commonscat": "Psyche by Wolf von Hoyer", "image": "Wolf von Hoyer, Psyche.jpg", "invno": "L 1853"}
# some interesting test invnos: '537', '688', '35', '698', '38'
#print(search_for_creator(sys.argv[1]))



# agenda
# * handle not matched invno better: how?
# * process creation data before QuickStatements conversion(?)
# * handle artwork groups
# * get the collection property (P195) from bstgs_inventory.json and get a source for P217 and P195

