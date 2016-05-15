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
                  proposallist=None, inputstrlist=None, entitytype='item',
                  givebackstrings=[], lastusedgroup=None):
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
    # Add the last used entities to the proposallist
    # if lastusedgroup is given
    # FIXME: Doubled proposals from last used and proposallist are not elegant!
    if not proposallist:
        proposallist = []
    if lastusedgroup:
        try:
            with open('data/wd_last_used_entities.json', 'r') as readfile:
                lastused = json.load(readfile)
        except (FileNotFoundError):
            lastused = {}
        if lastusedgroup in lastused:
            for i in range(min([len(lastused[lastusedgroup]), 5])):
            # max 5 more proposals
                proposallist.append({'text':
                    lastused[lastusedgroup][i]['label'],
                    'id': lastused[lastusedgroup][i]['id']})
    # Begin with matching
    while 'response' not in locals():
        # Construct elementary question
        question = ('Enter one of the following:\n'
                    '- a string to search Wikidata for or\n'
                    '- "Enter" to abort!')
	# Add the proposals to question if proposallist is given
        abc = 'abcdefghijklmnopqrstuvwxyz'
        if proposallist:
            proposaltext = 'The folling values are proposed:\n'
            for i in range(len(proposallist)):
                proposaltext += (style.select + abc[i] + ' ' +
                                 proposallist[i]['text'] + ' (' +
                                 proposallist[i]['id'] + ')\n' + style.end)
            question = proposaltext + question
            question = question.replace('- a string', '- the letter of the ' +
                'correct proposed entity,\n- a string')
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
                question = question.replace('- a string','- the number of the '
                            'correct entity,\n- a string')
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
                    matchesstr += (style.select + str(i+1) + ' ' + label +
                                   ' – ' + description + ' (' +
                                   possiblematches[i]['id'] + ')\n' +style.end)
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
        ## Give the string back if it is in givebackstrings
        if answer in givebackstrings:
            response = answer
        ## Abort if string is empty
        elif answer == '':
            if searchstr0:
                response = '[' + str(searchstr0) + ']'
            else:
                response = None
        ## Proposal confirmed with letter
        elif proposallist and answer in list(i for i in
                abc[:(len(proposallist))]):
            response = proposallist[abc.find(answer)]['id']
            responselabel = proposallist[abc.find(answer)]['text']
        ## Number of possible match entered
        elif 'possiblematches' in locals() and matchindex in range(0,
                len(possiblematches)):
            newmatchedid = possiblematches[matchindex]['id']
            response = newmatchedid
            responselabel = possiblematches[matchindex]['label']
        ## New search string entered
        else:
            searchstr = answer
    # Write matched ID to last used entities file
    if 'responselabel' in locals() and lastusedgroup:
        lastusedentity = {'label': responselabel, 'id': response}
        if lastusedgroup not in lastused:
            lastused[lastusedgroup] = []
        lastused[lastusedgroup][0:0] = [lastusedentity]
        if lastused[lastusedgroup].count(lastusedentity) > 1:
            lastused[lastusedgroup].reverse()
            del(lastused[lastusedgroup][
                lastused[lastusedgroup].index(lastusedentity)])
            lastused[lastusedgroup].reverse()
        with open('data/wd_last_used_entities.json', 'w+') as writefile:
            writefile.write(json.dumps(lastused, ensure_ascii=False,
                            indent=4, sort_keys=True))
    # Write newly matched ID to mapping file
    if 'newmatchedid' in locals() and searchstr0:
        mapping[searchstr0] = newmatchedid
        with open(mappingjsonfile, 'w+') as writefile:
            writefile.write(json.dumps(mapping, ensure_ascii=False,
                            indent=4, sort_keys=True))
    return response

class TestMatchWDItem(unittest.TestCase): # TODO!
  def test_str(self):
      self.assertEqual(match_wd_item('en', searchstr='Daniel Nikolaus Runge', 
                       inputstrlist=['1']),'Q1161913')


def get_wd_property_data(prop):
    try:
        with open('data/wd_props_datatypes.json', 'r') as readfile:
            allpropsdata = json.load(readfile)
    except (TypeError, FileNotFoundError):
        allpropsdata = {}
    if prop in allpropsdata:
        propdata = allpropsdata[prop]
    else:
        rawpropdata = json.loads(urllib.request.urlopen(
            'https://www.wikidata.org/wiki/Special:EntityData/' + prop +
            '.json').read().decode('utf-8'))
        label = (
            rawpropdata['entities'][prop]['labels']['en']['value'])
        datatype = (
            rawpropdata['entities'][prop]['datatype'])
        propdata = {'label': label, 'datatype': datatype}
        allpropsdata[prop] = propdata
        # Write newly fetched data to file
        with open('data/wd_props_datatypes.json', 'w+') as writefile:
            writefile.write(json.dumps(allpropsdata, ensure_ascii=False,
                            indent=4, sort_keys=True))
    return propdata


def add_value(addingprop, valueproposallist=None, lastusedgroup=None):
    """Find a value for a statement, qualifier or source"""
    # TODO: not stable, integrate into Statement()?
    propdata = get_wd_property_data(addingprop)
    addingpropref = '"' + propdata['label'] + '" (' + addingprop + ')'
    print('The datatype of ' + addingpropref + ' is ' +
          propdata['datatype'] + '. ', end='')
    if propdata['datatype'] == 'wikibase-item':
        print('What is the value for ' + addingpropref + '? ', end='')
        value = match_wd_item('en', proposallist=valueproposallist,
                              lastusedgroup=lastusedgroup)
    else:
        value = sinput('Enter the value!\n')
    return value

class Statement():
    def __init__(self, prop=None, value=None):
        self.prop = prop
        self.value = value
        self.quals = {}
        self.srcs = []
    # better add value instead of predifining it! TODO
    def add_value(self):
        pass
    def add_qual(self):
        qualprop = match_wd_item('en', entitytype='property',
            lastusedgroup='qualprops')
        qualvalue = add_value(qualprop, lastusedgroup=qualprop)
        self.quals[qualprop]= qualvalue
    def add_src(self): # TODO
        self.srcs.append([])
    def add_src_stmt(self): # TODO
        srcprop = match_wd_item('en', entitytype='property',
            lastusedgroup='srcprops')
    def make_dict(self):
        self.stmtdict = {'value': value}
        if self.quals:
            qualdict = {}
            for qualprop in self.quals:
                qualdict[qualprop] = self.quals[qualprop]
            self.stmtdict['quals'] = qualdict
        # srcs the same TODO
        return self.stmtdict

def add_statement(itemdict, addingpropid=None, forceadd=False,
                  valueproposallist=None):
    """Add something to a given dictionary for an item

    Labels, aliases, descriptions, notes and statements may be added.
    
    If the property is given and the datatype of the property is \
    wikibase-item, a list with proposals for the value coming from \
    match_wd_item may be given.
    """
    # The variable names in this function could be better, more like:
    # addingstmtprop, addingstmtvalue, addingqual…, addingsrc… TODO
    abort = False
    # Look for a property if none is given
    if not addingpropid:
        print('Do you want to edit the item? Change a label with ".", an ' +
              'alias with ",", a description with "+", add a note with "#" ' +
              'or add a property with the following instructions!')
        # FIXME: messy!
        addingpropid = match_wd_item('en', entitytype='property',
            givebackstrings=['.', ',', '+', '#'],
            lastusedgroup='stmtprops')
    # Ask for a value and save the value to the property
    if addingpropid != None:
        # Change label
        if addingpropid == '.':
            language = sinput('Enter the language code for the label!\n')
            label = sinput('Enter the label!\n')
            itemdict['labels'][language] = label
        # Change alias
        elif addingpropid == ',':
            language = sinput('Enter the language code for the alias!\n')
            alias = sinput('Enter the alias!\n')
            itemdict['aliases'][language] = alias
        # Change description
        elif addingpropid == '+':
            language = sinput('Enter the language code for the description!\n')
            description = sinput('Enter the description!\n')
            itemdict['descriptions'][language] = description
        # Add note
        elif addingpropid == '#':
            noteaddition = sinput('Enter the note!\n')
            itemdict['notes'].append('# NOTE: ' + noteaddition)
        # Add statement with given property
        else: # TODO: use add_value
            propdata = get_wd_property_data(addingpropid)
            addingpropref = '"' + propdata['label'] + '" (' + addingpropid + ')'
            print('The datatype of ' + addingpropref + ' is ' +
                  propdata['datatype'] + '. ', end='')
            if propdata['datatype'] == 'wikibase-item':
                print('What is the value for ' + addingpropref + '? ', end='')
                value = match_wd_item('en', proposallist=valueproposallist,
                                      lastusedgroup=addingpropid)
            else:
                value = sinput('Enter the value!\n')
            # Add statement if a value is given or adding is forced
            if value or forceadd == True:
                # Create property dictionary if not existing
                if addingpropid not in itemdict['statements']:
                    itemdict['statements'][addingpropid] = []
                # Add new statement to property dictionary
                stmt = Statement(addingpropid, value)
                itemdict['statements'][addingpropid].append({'value': value})
                # Adding qualifiers or sources # TODO
                qualsrcadding = 1
                while qualsrcadding:
                    pass
                    qualsrcadding = sinput('Type "q" if you want to add a qualifier or ' +
                        '"s" if you want to add a statement to the source or "ss" if ' +
                        'you want to add a new source!\n')
                    if qualsrcadding == 'q':
                        stmt.add_qual()
                    elif qualsrcadding == 's':
                stmtdict = stmt.make_dict()
                print('stmtdict: ', stmtdict)
    # If nothing to add is given exit with abort=True
    else:
        abort = True
    return itemdict, abort

def process_bstgs_creator(inputcreator):
    creator = {}
    creator['value'] = match_wd_item('de', searchstr=inputcreator['value'],
              mappingjsonfile='data/bstgs_wd_creator_mapping.json')
    if 'qualifiers' in inputcreator:
        creatorqualifierdict = {'Art des': ['P1777'],
                                'Kopie nach': ['P1877'],
                                'Nach': ['P1877'],
                                'Nachahmer': ['P1777'],
                                'Nachfolger': ['P1775'],
                                'Schule': ['P1780'],
                                'Umkreis': ['P1776'],
                                'vermutlich': ['P1779'],
                                'Werkstatt': ['P1774'],
                                'zugeschrieben': ['P1773'],
                                '?': ['P1779'],
                                'Anonymer Meister seiner Werkstatt': ['P1774'],
                                'Werkstatt?': ['ERROR NO MAPPING: Werkstatt?'],
                                # FIXME: Wikidata ontology is not sufficient
                                'Replik': ['P1877'],
                                'Werkstattkopie': ['P1774', 'P1877']}
        for qualifier in inputcreator['qualifiers']:
            proplist = creatorqualifierdict[qualifier]
            qualvalue = match_wd_item('de',
                searchstr=inputcreator['qualifiers'][qualifier],
                mappingjsonfile='data/bstgs_wd_creator_mapping.json')
            creator['qualifiers'] = [{prop: qualvalue} for prop in proplist]
    return creator

def unite(inputdict):
    """Unite the data of Wikidata, the BStGS inventory list and given \
    data for an artworkgroup

    Currently only the first inventory number (P217) in inputlist is \
    processed.
    """ # TODO: Handle artworkgroups: more P217 in inputlist and WD
    # Initialize the united dictionary for the artwork
    uniteddict = inputdict
    uniteddict['labels'] = {}
    uniteddict['aliases'] = {}
    uniteddict['descriptions'] = {}
    uniteddict['notes'] = []
    # Match the dictionary against other sources
    if 'P217' in inputdict['statements']:
        # Wikidata
        for item in items:
            if inputdict['statements']['P217'][0]['value'] in item['invno']:
            # TODO: matches also groups atm
                uniteddict['wdqid'] = ('Q' + str(item['wdqid']))
        # BStGS inventory list
        if inputdict['statements']['P217'][0]['value'] in list(
              artwork['invno'] for artwork in bstgsinventory):
            for artwork in bstgsinventory:
            # TODO: Find better solution instead of this double checking!
                if inputdict['statements']['P217'][0]['value'] == (
                        artwork['invno']):
                    print('BStGS inventory title: ' + style.source +
                          artwork['title'] + style.end + 
                          ', BStGS inventory creator: ' + style.source +
                          str(artwork['creator']) + style.end)
                    uniteddict['statements']['P217'][0]['qualifiers'] = [{'P195': 'Q812285'}]
                    uniteddict['labels']['de'] = artwork['title']
                    # Construct source
                    sourcetimeqs = '+0000000' + artwork['stime'][:-7] + 'Z/13'
                    source = [{
                        'P854': artwork['sURL'],
                        'P813': sourcetimeqs,
                        'P123': 'Q812285',
                        'P407': 'Q188'}]
                    # The title (P1476), e.g. "Bestandsliste der
                    # Bayerischen Staatsgemäldesammlungen A-E" and the
                    # page (P304) as a string with a hyphen for a range
                    # could theoretically be given here.
                    uniteddict['statements']['P217'][0]['sources'] = source
                    # P170
                    creator = process_bstgs_creator(artwork['creator'])
                    creator['sources'] = source
                    if 'P170' not in uniteddict['statements']:
                        uniteddict['statements']['P170'] = []
                    uniteddict['statements']['P170'].append(creator)
                    # P195
                    if 'P195' not in uniteddict['statements']:
                        uniteddict['statements']['P195'] = []
                    uniteddict['statements']['P195'].append(
                        {'value': 'Q812285', 'sources': source})
        else:
            uniteddict['notes'].append('# WARNING: The inventory number ' +
                                       'was not found in the inventory!')
            print('No inventory entry found for inventory number: ',
                  inputdict['statements']['P217'][0]['value'])
    else:
        print('No inventory number was given.')

    # Add P31 and arbitrary other statments TODO: better Commons parsing?
    ## P31
    uniteddict, abort = add_statement(uniteddict, addingpropid='P31',
        forceadd=True)
    ## arbitrary other labels, aliases, descriptions, notes, statements
    abort = False
    while not abort:
        uniteddict, abort = add_statement(uniteddict)

    return uniteddict


def construct_qsvalue(value, prop):
    if not value:
        value = '[' + str(value) + ']'
    else:
        if get_wd_property_data(prop)['datatype'] in ['wikibase-item', 'time',
              'globe-coordinate', 'quantity']:
            pass
        else:
            value = '"' + value + '"'
    return value
    
def artworkjson2qs(artworkjson):
    """Convert the collection to QuickStatements format"""
    # Initialize
    outputstr = ''
    # Add notes
    if 'notes' in artworkjson:
        outputstr += ('\n'.join(artworkjson['notes']) + '\n')
    # Add creation command and prepare reference to item for statements
    if 'wdqid' in artworkjson:
        ref = artworkjson['wdqid']
    else:
        outputstr += 'CREATE\n'
        ref = 'LAST'
    # Add labels, aliases and descriptions
    for kind in ['labels','aliases','descriptions']:
        for language in artworkjson[kind]:
            outputstr += (ref + '\t' + kind[0].upper() + language + '\t"' +
                          artworkjson[kind][language] + '"\n')
    # Add statements
    for prop in artworkjson['statements'].keys():
        if prop not in ['fulltitle', 'notes', 'Lde']:
            for statement in artworkjson['statements'][prop]:
                # Add value
                outputstr += (ref + '\t' + prop + '\t' +
                              construct_qsvalue(statement['value'], prop))
                # Add qualifiers
                if 'qualifiers' in statement:
                    for qualifier in statement['qualifiers']:
                        for qualprop in qualifier:
                            outputstr += ('\t' + qualprop + '\t' +
                                          construct_qsvalue(
                                          qualifier[qualprop], qualprop))
                # Add one source prop-value pair
                # FIXME: Unfortunately QuickStatements is restricted here!
                # Use pywikibot
                if 'sources' in statement:
                    for source in statement['sources']:
                        if 'P854' in source:
                            outputstr += ('\tS854\t' +
                                construct_qsvalue(source['P854'], 'P854'))
                outputstr += '\n'
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
        process_single({'statements':{'P217': [{'value': inputinvno}]}})
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
# * introduce more relative variables which reduces bugs for incorrect referencing!!!
# * introduce abbreviations stmt, prop, qual, src. value stays
# * put BStGS stuff in own module!
#     * and remove --invno option instead of input with collection like:
#       {'P217': ['quals': {'P195': '[collection]'}, 'value': '[invno]']}
# * add qualifiers and sources support to add_statement
# * handle artwork groups: probably just print a warning!
# * perhaps rewrite to match from arbitrary sources and with other things than invno perhaps


