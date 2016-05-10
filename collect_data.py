#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request, urllib.parse, urllib.error
import readline
import unittest


class style: # ansi text styling
    source = '\033[92m' # bright green
    select = '\033[93m' # bright yellow
    inputting = '\033[4m' # underline
    end = '\033[0m'
def sinput(prompt):
    """Styled input"""
    s = input(prompt + style.inputting)
    print(style.end, end='')
    return s


## Read data from the BStGS inventory list and the Wikidata list of
## inventory numbers json files
items = json.load(open('data/wd_invnos.json', 'r'))
bstgsinventory = json.load(open('data/bstgs_inventory.json', 'r'))


def search_wd_items(searchstr, language, entitytype='item'):
    """"Search for an item on Wikidata based on a given string"""
    searchstr.replace(' ','+')
    params = urllib.parse.urlencode({'search': searchstr,
                                     'action': 'wbsearchentities',
                                     'language': language,
                                     'format': 'json',
                                     'type': entitytype})
    f = urllib.request.urlopen('http://www.wikidata.org/w/api.php?' + params)
    f = f.read().decode('utf-8')
    g = json.loads(f)
    possiblematches = g['search']
    return possiblematches

def match_wd_item(language, searchstr=None, mappingjsonfile=None,
                  proposallist=None, inputstrlist=None, entitytype='item'):
    """Try to find a Wikidata item, e.g. by searching with a string

    The function gives the user the following input options to select an item:
    - (number of one of the possible matches if a previous search has found \
    possible matches)        -> response -> map!
    - (new) WD-search-string -> search_wd_items()
    - abort                  -> response is "[search-string]"

    * mappingjsonfile is used to use a mapping file for successful matches
    * proposallist is used to give a list of (for now max. 26) proposed \
      matches which might be confirmed by the user, each proposal has to be a \
      dictionary holding the Wikidata entity ID in the "id" key and a \
      description in the "text" key
    * inputstrlist is used to give a list of input strings for unit testing
    """
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
            question = question.replace('- a "string', '- the letter of the ' +
                'correct proposed entity,\n- a "string')
        # Process the optional search string if given
        if searchstr:
        ## Look in the mapping for the search string
            if searchstr in mapping:
                response = mapping[searchstr]
                break
            possiblematches = search_wd_items(searchstr, language, entitytype)
        ## Add text to question if a Wikidata search has yet taken place
            if len(possiblematches) == 0:
                question = ('The search for "' + searchstr + '" has not found '
                            'any possible matches.\n' + question)
            else:
                question = question.replace('- a "string','- the number of the '
                            'correct entity,\n- a "string')
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
        if inputstrlist: # for unit testing
            answer = inputstrlist[inputstrno]
            inputstrno += 1
        else:
            print(question)
            answer = sinput('')
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
            if searchstr0:
                response = '[' + str(searchstr0) + ']'
            else:
                response = None
        ## Proposal confirmed with "y"
        elif proposallist and answer in list(i for i in
                abc[:(len(proposallist))]):
            response = proposallist[abc.find(answer)]['id']
        ## Number of possible match entered
        elif 'possiblematches' in locals() and matchindex in range(0,
                len(possiblematches)):
            newmatchedid = possiblematches[matchindex]['id']
            response = newmatchedid
        ## New search string entered
        elif answer[0] == answer[-1] == '"':
            searchstr = answer[1:-1]
        ## Abort
        else:
            if searchstr0:
                response = '[' + str(searchstr0) + ']'
            else:
                response = None
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


def add_statement(itemdict, addingpropid=None, forceadd=False,
                  valueproposallist=None):
    """Add a statement to a given dictionary for an item
    
    If the property is given and the datatype of the property is \
    wikibase-item, a list with proposals for the value coming from \
    match_wd_item may be given.
    """
    abort = False
    # Look for a property if none is given
    if not addingpropid:
        print('Is there another property you want to add?')
        addingpropid = match_wd_item('en', entitytype='property',
            proposallist=[{'id': 'P180', 'text': 'depicts'}])
    # If property is given look for a value
    if addingpropid != None:
        addingpropdata = json.loads(urllib.request.urlopen(
            'https://www.wikidata.org/wiki/Special:EntityData/' + addingpropid+
            '.json').read().decode('utf-8'))
        addingpropdatatype = (
            addingpropdata['entities'][addingpropid]['datatype'])
        addingproplabel = (
            addingpropdata['entities'][addingpropid]['labels']['en']['value'])
        addingpropref = '"' + addingproplabel + '" (' + addingpropid + ')'
        print('The datatype of ' + addingpropref + ' is ' +
              addingpropdatatype + '.')
        if addingpropdatatype == 'wikibase-item':
            print('What is the value for ' + addingpropref + '?')
            value = match_wd_item('en', proposallist=valueproposallist)
        else:
            value = sinput('Enter the value!\n\n')
        # Add statement if a value is given or adding is forced
        if value or forceadd == True:
            # Create property dictionary if not existing
            if not itemdict.get(addingpropid):
                itemdict[addingpropid] = []
            # Add new statement to property dictionary
            itemdict[addingpropid].append(value)
    # If no property is given exit with abort=True
    else:
        abort = True
    return itemdict, abort

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
                    print('BStGS inventory title: ' + artwork['title'])
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

    # Add P31, P195 and arbitrary other statments TODO: better Commons parsing?
    ## P31
    uniteddict, abort = add_statement(uniteddict, addingpropid='P31',
        forceadd=True, valueproposallist=
            [{'id': 'Q3305213', 'text': 'painting'},
             {'id': 'Q860861', 'text': 'sculpture'}])
    ## P195
    uniteddict, abort = add_statement(uniteddict, addingpropid='P195',
        forceadd=True, valueproposallist=
            [{'id': 'Q812285', 'text': 'Bavarian State Painting Collections'}])
    ## arbitrary other statements
    abort = False
    while not abort:
        uniteddict, abort = add_statement(uniteddict)
    # Add a note
    note = sinput('Enter a note or abort with "Enter"!\n')
    if note:
        uniteddict['note'] = note

    return uniteddict

def artworkjson2qs(artworkjson):
    """Convert the collection to QuickStatements format"""
    artworkjson = {key:'[None]' if artworkjson[key] is None else
                  artworkjson[key] for key in list(artworkjson.keys())}
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
        creator = match_wd_item('de', searchstr=creator,
                  mappingjsonfile='data/bstgs_wd_creator_mapping.json')
        if 'qualifiers' in artworkjson['creator']:
            creatorqualifierdict = {'Kopie nach': 'P1877',
                                    'zugeschrieben': 'P1773'}
            for key in creatorqualifierdict:
                if key in artworkjson['creator'].get('qualifiers'):
                    #TODO: output the string in () if it could not be mapped
                    creatorinqualifier = artworkjson['creator']['qualifiers']\
                                         [key]
                    creatorinqualifier = match_wd_item('de',
                        searchstr=creatorinqualifier,
                        mappingjsonfile='data/bstgs_wd_creator_mapping.json')
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
        outputstr += '\n'
    print(artworkjson) # TODO: testing
    for prop in artworkjson.keys():
        if prop not in ['invno', 'invno not found in inventory', 'creator',
                        'title', 'stime', 'sURL', 'fulltitle', 'note']:
            for value in artworkjson[prop]:
                if not value:
                    value = '[' + str(value) + ']'
                outputstr += (ref + '\t' + prop + '\t' + value + '\n')
    return outputstr


def try_write_file(outputfile, output, overwrite=False):
    """Try to write a file and ask to overwrite it if it yet exists"""
    try:
        with open(outputfile, 'x') as f:
            f.write(output)
    except FileExistsError:
        if overwrite == False:
            overwrite = sinput('The file "' + outputfile +
            '" exists yet. Press "y" if you want to overwrite it! ')
            if overwrite != 'y':
                pass
            else:
                with open(outputfile, 'w+') as f:
                    f.write(output)
    return overwrite

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
# * handle artwork groups: probably just print a warning!
# * get the collection property (P195) from bstgs_inventory.json and get a source for P217 and P195
# * perhaps rewrite to match from arbitrary sources and with other things than invno perhaps

