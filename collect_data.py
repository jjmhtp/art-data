#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request, urllib.parse, urllib.error

## Read data from the BStGS inventory list and the Wikidata list of
## inventory numbers json files
items = json.load(open('data/wd_invnos.json', 'r'))
bstgsinventory = json.load(open('data/bstgs_inventory.json', 'r'))

## Function to unite collected data
def unite(inputdict):
    """unite the data of Wikidata, the BStGS inventory list and given \
    data for an artworkgroup""" # TODO: for now an artworkgroup(?)
    uniteddict = inputdict
    if 'invno' in inputdict:
        # Wikidata
        for item in items:
            if inputdict['invno'] in item['invno']:
            # TODO: matches also groups atm
                uniteddict['wdqid'] = ('Q' + str(item['wdqid']))
        # BStGS inventory list
        if inputdict['invno'] in list(artwork['invno'] for artwork in
                                      bstgsinventory):
            for artwork in bstgsinventory:
            # TODO: Find better solution instead of this double checking!
                if inputdict['invno'] == artwork['invno']:
                    uniteddict['creator'] = artwork['creator']
                    uniteddict['title'] = artwork['title']
                    uniteddict['sURL'] = artwork['sURL']
                    uniteddict['stime'] = artwork['stime']
        else:
            uniteddict['invno not found in inventory'] = True
            print('No inventory entry found for inventory number: ',
                  inputdict['invno'])
    else:
        print('No inventory number was given.')
    return uniteddict

## Search for a creator on Wikidata based on a given string
def search_wd_entities(searchstr, language):
    searchstr.replace(' ','+')
    params = urllib.parse.urlencode({'search': searchstr,
                                     'action': 'wbsearchentities',
                                     'language': language, 'format': 'json'})
    f = urllib.request.urlopen('http://www.wikidata.org/w/api.php?' + params)
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
    question += ('Enter the number of the correct item or the QID of the '
                 'correct item or a "new string to search Wikidata for" in '
                 'double quotes or abort with anything else!\n')
    if len(possiblematches) == 0:
        question = ('The search for "' + searchstr + '" has not found any '
                    'possible matches. Enter the QID of the correct item or a '
                    '"new string to search Wikidata for" in double quotes or '
                    'abort with anything else!\n')
    return question, possiblematches

## Try to match a given search string to a Wikidata item with manual checking
def try_matching_str_to_wd(searchstr, language, mappingjsonfile):
    searchstr0 = searchstr
    try:
        with open(mappingjsonfile, 'r') as readfile:
            mapping = json.load(readfile)
    except (FileNotFoundError, ValueError):
        mapping = {}
    if searchstr in mapping:
        response = mapping[searchstr]
    else:
        while 'response' not in locals():
            question, possiblematches = search_wd_entities(searchstr, language)
            answer = input(question)
            print('')
            matchindex = -1
            try:
                matchindex = int(answer) - 1
            except:
                pass
            # abort
            if answer == '':
                response = '[' + searchstr0 + ']'
            # number of possible match entered
            elif matchindex in range(0, len(possiblematches)):
                newmatchedid = possiblematches[matchindex]['id']
                response = newmatchedid
            # QID entered
            elif (answer[0] == 'Q' and set(answer[1:] + '0123456789') ==
                  {'0','1','2','3','4','5','6','7','8','9'}): # not using re
                newmatchedid = answer
                response = newmatchedid
            # new search string entered
            elif answer[0] == answer[-1] == '"':
                searchstr = answer[1:-1]
            # abort
            else:
                response = '[' + searchstr0 + ']'
        if 'newmatchedid' in locals():
            # write newly matched ID to mapping file
            mapping[searchstr0] = newmatchedid
            with open(mappingjsonfile, 'w+') as writefile:
                writefile.write(json.dumps(mapping, ensure_ascii=False,
                                           indent=4, sort_keys=True))
    return response

## Convert the collection to QuickStatements format
def artworkjson2qs(artworkjson):
    outputstr = ''
    # Add warning if the inventory number could not be found in the inventory
    commentOutStr = ''
    if 'invno not found in inventory' in artworkjson:
        commentOutStr = '# '
        outputstr = (commentOutStr + 'WARNING: The inventory number was not '
                     'found in the inventory!\n' + outputstr)
    # Prepare extension of existing and creation of new items
    if 'wdqid' in artworkjson:
        ref = commentOutStr + artworkjson['wdqid']
    else:
        outputstr += commentOutStr + 'CREATE\n'
        ref = commentOutStr + 'LAST'
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
    # Add statement constructors
    if 'title' in artworkjson:
        outputstr += (ref + '\tLde\t"' + artworkjson['title'] + '"\n')
    if 'creator' in artworkjson:
        outputstr += (ref + '\tP170\t' + creator + '\n')
    if 'invno' in artworkjson:
        outputstr += (ref + '\tP217\t"' + artworkjson['invno'] +
                  '"\tP195\tQ812285\tS854\t"' + artworkjson['sURL'] +
                  '"\tS813\t"+0000000' + artworkjson['stime'][:-7] +
                  'Z/13"\tS123\tQ812285\tS407\tQ188\n')
    # S1476 "Bestandsliste der Bayerischen Staatsgemäldesammlungen A-E"
    # TODO: S304 [string for page]: hyphen for ranges
    if 'instanceOf' in artworkjson:
        outputstr += (ref + '\tP31\t' + artworkjson['instanceOf'] + '\n')
    if 'image' in artworkjson:
        outputstr += (ref + '\tP18\t"' + artworkjson['image'] + '"\n')
    if 'commonscat' in artworkjson:
        outputstr += (ref + '\tP373\t"' + artworkjson['commonscat'] + '"\n')
    if 'depicts' in artworkjson:
        outputstr += (ref + '\tP180\t' + artworkjson['depicts'] + '\n')
    #TODO: non-unique properties such as P180 should be able to have >1 value
    return outputstr

## Try to write a file and ask to overwrite it if it yet exists
def try_write_file(outputfile, output):
    try:
        with open(outputfile, 'x') as f:
            f.write(output)
    except FileExistsError:
        answer = input('The file "' + outputfile +
                       '" exists yet. Press "y" if you want to overwrite it! ')
        if answer == 'y':
            with open(outputfile, 'w+') as f:
                f.write(output)

def process_single(inputdict):
        uniteddict = unite(inputdict)
        print(json.dumps(uniteddict, ensure_ascii=False, indent=4))
        print(artworkjson2qs(uniteddict))

def process_multiple(inputdictlist, inputname=None, outputfileplusforce=None,
                     outputfileqsforce=None):
    # Without 'inputname' the other two parameter are required.
    """Process multiple items and write the augmented JSON and \
    QuickStatements results to files."""
    outputdictlist = []
    outputqs = ''
    for inputdict in inputdictlist:
        uniteddict = unite(inputdict)
        outputdictlist.append(uniteddict)
        outputqs += artworkjson2qs(uniteddict) + '\n'
    # Determine names of output files
    if inputname:
        outputfileplus = inputname.rsplit('.json')[0] + '_plus.json'
        outputfileqs = inputname.rsplit('.json')[0] + '_qs.txt'
    if outputfileplusforce:
        outputfileplus = outputfileplusforce
    if outputfileqsforce:
        outputfileqs = outputfileqsforce
    # Write files
    try_write_file(outputfileplus,
                   json.dumps(outputdictlist, ensure_ascii=False, indent=4))
    try_write_file(outputfileqs, outputqs)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--invno')
    parser.add_argument('--json')
    parser.add_argument('-i', '--inputjsonfile')
    parser.add_argument('-oplus', '--outputfileplus')
    parser.add_argument('-oqs', '--outputfilequickstatements')
    args = parser.parse_args()
    
    inputinvno = args.invno
    if inputinvno:
        process_single({'invno': inputinvno})
    
    inputjson = args.json
    if inputjson:
        process_single(json.loads(inputjson))
    
    inputjsonfile = args.inputjsonfile
    if inputjsonfile:
        inputdictlist = json.load(open(inputjsonfile, 'r'))
        process_multiple(inputdictlist, inputname=args.inputjsonfile,
            outputfileplusforce=args.outputfileplus,
            outputfileqsforce=args.ouputfilequickstatements)




# agenda
# * process creation data before QuickStatements conversion(?)
# * handle artwork groups
# * get the collection property (P195) from bstgs_inventory.json and get a source for P217 and P195
# * perhaps rewrite to match from arbitrary sources and with other things than invno perhaps

