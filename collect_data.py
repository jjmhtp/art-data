#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request, urllib.parse, urllib.error
import unittest

## Read data from the BStGS inventory list and the Wikidata list of
## inventory numbers json files
items = json.load(open('data/wd_invnos.json', 'r'))
bstgsinventory = json.load(open('data/bstgs_inventory.json', 'r'))

## Function to unite collected data
def unite(inputdict):
    """Unite the data of Wikidata, the BStGS inventory list and given \
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



def search_wd_entities(searchstr, language):
    """"Search for an item on Wikidata based on a given string"""
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

def search_wd_items(searchstr, language):
    """"Search for an item on Wikidata based on a given string"""
    searchstr.replace(' ','+')
    params = urllib.parse.urlencode({'search': searchstr,
                                     'action': 'wbsearchentities',
                                     'language': language, 'format': 'json'})
    f = urllib.request.urlopen('http://www.wikidata.org/w/api.php?' + params)
    f = f.read().decode('utf-8')
    g = json.loads(f)
    possiblematches = g['search']
    return possiblematches

def match_wd_item(language, searchstr=None, mappingjsonfile=None,
                  proposallist=None, inputstrlist=None):
    """Try to find a Wikidata item, e.g. by searching with a string

    The function gives the user the following input options to select an item:
    - (number of one of the possible matches if a previous search has found \
    possible matches)        -> response -> map!
    - WD-QID                 -> response -> map!
    - (new) WD-search-string -> search_wd_items()
    - abort                  -> response is "[search-string]"

    * mappingjsonfile is used to use a mapping file for successful matches
    * proposallist is used to give a list of (for now max. 26) proposed \
      matches which might be confirmed by the user, each proposal has to be a \
      dictionary holding the Wikidata QID in the "id" key and a description \
      in the "text" key
    * inputstrlist is used to give a list of input strings for unit testing
    """
    """Replacement for try_matching_str_to_wd()""" # TODO: remove!
    inputstrno = 0 # begin with first item of inputstrlist
    searchstr0 = searchstr
    # Load the optional mapping file if given and found
    try:
        with open(mappingjsonfile, 'r') as readfile:
            mapping = json.load(readfile)
    except (TypeError, FileNotFoundError):
        mapping = {}
    # Begin with matching
    while 'response' not in locals():
        # Construct elementary question
        question = ('Enter one of the following:\n'
                    '- the QID of the correct item,\n'
                    '- a "string to search Wikidata for in double quotes" or\n'
                    '- anything else to abort!\n')
	# Add the proposals to question if proposallist is given
        abc = 'abcdefghijklmnopqrstuvwxyz'
        if proposallist:
            proposaltext = 'The folling values are proposed:\n'
            for i in range(len(proposallist)):
                proposaltext += (abc[i] + ' ' + proposallist[i]['text'] +
                                 ' (' + proposallist[i]['id'] + ')\n')
            question = proposaltext + question
            question = question.replace('- the QID', '- the letter of the ' +
                'correct proposed item,\n- the QID')
        # Process the optional search string if given
        if searchstr:
        ## Look in the mapping for the search string
            if searchstr in mapping:
                response = mapping[searchstr]
                break
            possiblematches = search_wd_items(searchstr, language)
        ## Add text to question if a Wikidata search has yet taken place
            if len(possiblematches) == 0:
                question = ('The search for "' + searchstr + '" has not found '
                            'any possible matches.\n' + question)
            else:
                question = question.replace('- the QID','- the number of the '
                            'correct item,\n- the QID')
                matchesstr = ('The search for "' + searchstr + '" has found ' +
                              str(len(possiblematches))+' possible matches:\n')
        ## Add a line for each possible match
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
                    matchesstr += (str(i+1) + ' ' + label + ' – ' +
                                   description + ' (' +
                                   possiblematches[i]['id'] + ')\n')
                question = matchesstr + question
        # Input prompt
        if inputstrlist:
            answer = inputstrlist[inputstrno]
            inputstrno += 1
        else:
            print(question)
            answer = input('  ')
            # The long question string breaks the ouput here on OS X otherwise
            print('')
        matchindex = -1
        try:
            matchindex = int(answer) - 1
        except ValueError:
            pass
        # Process the user entered answer
        ## Abort if string empty
        if answer == '':
            response = '[' + str(searchstr0) + ']'
        ## Proposal confirmed with "y"
        elif proposallist and answer in list(i for i in abc):
            response = proposallist[abc.find(answer)]['id']
        ## Number of possible match entered
        elif 'possiblematches' in locals() and matchindex in range(0,
                len(possiblematches)):
            newmatchedid = possiblematches[matchindex]['id']
            response = newmatchedid
        ## QID entered
        elif (answer[0] == 'Q' and set(answer[1:] + '0123456789') ==
              {'0','1','2','3','4','5','6','7','8','9'}): # not using re
            newmatchedid = answer
            response = newmatchedid
        ## New search string entered
        elif answer[0] == answer[-1] == '"':
            searchstr = answer[1:-1]
        ## Abort
        else:
            response = '[' + str(searchstr0) + ']'
    # write newly matched ID to mapping file
    if 'newmatchedid' in locals() and searchstr0:
        mapping[searchstr0] = newmatchedid
        try:
            with open(mappingjsonfile, 'w+') as writefile:
                writefile.write(json.dumps(mapping, ensure_ascii=False,
                                indent=4, sort_keys=True))
        except (TypeError):
            pass
    return response

class TestMatchWDItem(unittest.TestCase): # TODO!
  def test_str(self):
      self.assertEqual(match_wd_item('en', searchstr='Daniel Nikolaus Runge', 
                       inputstrlist=['1']),'Q1161913')



def try_matching_str_to_wd(searchstr, language, mappingjsonfile):
    """Try to find a Wikidata item, e.g. by searching with a string"""
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
                  '"\tP195\tQ812285')
        if 'sURL' in artworkjson: # there is no source if invno wasn't matched
            outputstr += ('\tS854\t"' + artworkjson['sURL'])
                  # FIXME: Multiple statements for one source do not work in
		  # QuickStatements!
                  # + '"\tS813\t"+0000000' + artworkjson['stime'][:-7] +
                  # 'Z/13"\tS123\tQ812285\tS407\tQ188\n')
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
    # Unit testing, only used while testing (TODO)
    #unittest.main()
    # Fetch and process arguments:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--invno')
    parser.add_argument('--json')
    parser.add_argument('-i', '--inputjsonfile')
    parser.add_argument('-oplus', '--outputfileplus')
    parser.add_argument('-oqs', '--outputfilequickstatements')
    args = parser.parse_args()
    ## an inventory number
    inputinvno = args.invno
    if inputinvno:
        process_single({'invno': inputinvno})
    ## a json dictionary
    inputjson = args.json
    if inputjson:
        process_single(json.loads(inputjson))
    ## a json file with a list of dictionaries
    inputjsonfile = args.inputjsonfile
    if inputjsonfile:
        inputdictlist = json.load(open(inputjsonfile, 'r'))
        oqs = args.outputfilequickstatements # TODO: I get it just this way.
        process_multiple(inputdictlist, inputname=args.inputjsonfile,
            outputfileplusforce=args.outputfileplus,
            outputfileqsforce=oqs)




# agenda
# * process creation data before QuickStatements conversion(?)
# * handle artwork groups
# * get the collection property (P195) from bstgs_inventory.json and get a source for P217 and P195
# * perhaps rewrite to match from arbitrary sources and with other things than invno perhaps

