#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import json
import collect_data
from collect_data import style
from collect_data import sinput
import get_wd_bstgs


def catpages(catname):
    """Collect file and category pages from a Wikimedia Commons \
    category and return a dictionary with fields for either the file \
    or the category title and the full title of the page.
    """
    params = urllib.parse.urlencode({'language': 'commons', 'project':
        'wikimedia', 'categories': catname, 'ns[6]': '1', 'ns[14]': '1',
        'ext_image_data': '0', 'file_usage_data': '0', 'format': 'json',
	'doit': '1'})
    url = ('https://petscan.wmflabs.org/?' + params)
    f = urllib.request.urlopen(url)

    pages = json.loads(f.read().decode('utf-8'))
    pages = pages['*'][0]['a']['*']
    simplepages = []
    for i in range(len(pages)):
        simplepages.append({'fulltitle': pages[i]['nstext'] + ':' +
                            pages[i]['title'].replace('_', ' ')})
        simplepages[i]['statements'] = {}
        if pages[i]['nstext'] == 'File':
            simplepages[i]['statements']['P18'] = [{}]
            simplepages[i]['statements']['P18'][0]['value'] = (
                pages[i]['title'].replace('_', ' '))
        elif pages[i]['nstext'] == 'Category':
            simplepages[i]['statements']['P373'] = [{}]
            simplepages[i]['statements']['P373'][0]['value'] = (
                pages[i]['title'].replace('_', ' '))
    
    return simplepages

def invnos_for_cat(catname, writefiles=False):
    """Take the pages collected by catpages, let the user look for \
    corresponding inventory numbers and return a dictionary with the \
    pairs.
    """
    pages = catpages(catname)
    augmenteddictlist = []
    qsstring = ''
    overwritejson = False
    overwritejsonplus = False
    overwriteqs = False
    i = 0
    # Add inventory numbers
    while i < len(pages):
        params = urllib.parse.urlencode({'action': 'raw',
            'title': pages[i]['fulltitle']})
        url = 'https://commons.wikimedia.org/w/index.php?' + params
        f = urllib.request.urlopen(url)
        f = f.read().decode('utf-8')
        print('\n', pages[i]['fulltitle'], '\n', style.source + f + style.end)
        answer = ''
        while answer == '':
            answer = sinput('Please insert the inventory number! (Or input ' +
                            '"exit" to exit or "skip" to delete the entry!\n')
        # Stop looking for inventory numbers
        if answer == 'exit':
            break
        # Remove the page from the list
        elif answer == 'skip':
            del pages[i]
            print('The page has been skipped.')
        # Select from different images for one object
        elif 'P217' in pages[i-1]['statements'] and answer in (
              page['statements']['P217'] for page in pages[:i]):
            for j in range(i):
                if answer == pages[j]['statements']['P217']:
                    print('The following two pages belong to '
                        'the object with the inventory number ' + answer +
                        ': \n' + style.select + '1 ' + pages[j]['fulltitle'] +
                        '\n2 ' + pages[i]['fulltitle'] + style.end)
                    selection = ''
                    while selection != '1' and selection != '2':
                        selection = sinput('Please enter the number of the ' +
                                           'preferred one!\n')
                    selection = int(selection) - 1
                    duplicates = [pages[j],pages[i]]
                    print('duplicates: ', duplicates)
                    commoninvno = pages[j]['statements']['P217']
                    pages[j] = duplicates[selection]
                    pages[j]['statements']['P217'] = commoninvno
                    # TODO: simplify perhaps
         #           betterdup = duplicates.pop(selection)
         #           pages[i]['nstext'] = betterdup['nstext']
         #           pages[i]['title'] = betterdup['title']
         #           if 'notusedfiles' in pages[j].keys():
         #               pages[i]['notusedfiles'] += duplicates
         #           else:
         #               pages[i]['notusedfiles'] = duplicates
                    # TODO: improve evtl
                    print('i (eig neu): ',pages[i],'\nj (eig alt): ',pages[j])
                    del pages[i]
        # Simply add the inventory number and pass info to collect_data.unite
        else:
            pages[i]['statements']['P217'] = [{'value': answer}]

            uniteddict = collect_data.unite(pages[i])
            augmenteddictlist.append(uniteddict)
            qsstring += collect_data.artworkjson2qs(uniteddict) + '\n'

            i += 1

        # Write write the JSON, the augmented JSON and QuickStatements
        # results to files
        if writefiles == True:
            filenametrunk = 'data/objects-' + catname
            overwritejson = collect_data.try_write_file(filenametrunk +
                '.json', json.dumps(pages, ensure_ascii=False, indent=4,
                sort_keys=True), overwrite=overwritejson)
            overwritejsonplus = collect_data.try_write_file(filenametrunk +
                '_plus.json', json.dumps(augmenteddictlist,
                ensure_ascii=False, indent=4, sort_keys=True),
                overwrite=overwritejsonplus)
            overwriteqs = collect_data.try_write_file(filenametrunk +
                '_qs.txt', qsstring, overwrite=overwriteqs)

    return pages, augmenteddictlist, qsstring

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catname')
    args = parser.parse_args()

    # Renew Wikidata items
    get_wd_bstgs.get_wd_bstgs()

    # Fetch data from the Commons category, integrate it and write it to files
    invnos_for_cat(args.catname, writefiles=True)



