#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import json
import collect_data
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
        if pages[i]['nstext'] == 'File':
            simplepages[i]['image'] = pages[i]['title'].replace('_', ' ')
        elif pages[i]['nstext'] == 'Category':
            simplepages[i]['commonscat'] = pages[i]['title'].replace('_', ' ')
    
    return simplepages

def invnos_for_cat(catname):
    """Take the pages collected by catpages, let the user look for \
    corresponding inventory numbers and return a dictionary with the \
    pairs.
    """
    pages = catpages(catname)
    augmenteddictlist = []
    qsstring = ''
    i = 0
    # Add inventory numbers
    while i < len(pages):
        params = urllib.parse.urlencode({'action': 'raw',
            'title': pages[i]['fulltitle']})
        url = 'https://commons.wikimedia.org/w/index.php?' + params
        f = urllib.request.urlopen(url)
        f = f.read().decode('utf-8')
        print('\n', pages[i]['fulltitle'], '\n', f)
        answer = input('Please insert the inventory number! (Or input "exit" '
                       'to exit or "skip" to delete the entry!\n')
        # Stop looking for inventory numbers
        if answer == 'exit':
            break
        # Remove the page from the list
        elif answer == 'skip':
            del pages[i]
            print('The page has been skipped.')
        # Select from different images for one object
        elif 'invno' in pages[i-1] and answer in (page['invno'] for page in
              pages[:i]):
            for j in range(i):
                if answer == pages[j]['invno']:
                    print('The following two pages belong to '
                        # TODO: Better category processing?
                        'the object with the inventory number ' + answer +
                        ': \n1 ' + pages[j]['fulltitle'] + '\n2 ' + 
                        pages[i]['fulltitle'])
                    selection = ''
                    while selection != '1' and selection != '2':
                        selection = input('Please enter the number of the ' +
                        'preferred one!\n')
                    selection = int(selection) - 1
                    # TODO: print also URLs here!
                    duplicates = [pages[j],pages[i]]
                    print('duplicates: ', duplicates)
                    commoninvno = pages[j]['invno']
                    pages[j] = duplicates[selection]
                    pages[j]['invno'] = commoninvno
                    # TODO: simplify perhaps
         #           betterdup = duplicates.pop(selection)
         #           pages[i]['nstext'] = betterdup['nstext']
         #           pages[i]['title'] = betterdup['title']
         #           if 'notusedfiles' in pages[j].keys():
         #               pages[i]['notusedfiles'] += duplicates
         #           else:
         #               pages[i]['notusedfiles'] = duplicates
                    # TODO: improve evtl
                    print('i (eig neu): ', pages[i], '\nj (eig alt): ', pages[j])
                    del pages[i]
        # Simply add the inventory number and ask for other info
        # TODO: Why is this functionality not in collect_data.py?
        else:
            pages[i]['invno'] = answer
#            # Add instanceOf, depicts etc. # TODO: better Commons parsing?
#            ## instanceOf
#            print('What is the object instance of?')
#            pages[i]['instanceOf'] = collect_data.match_wd_item('en',
#                mappingjsonfile='data/object_classes_mapping.json',
#                proposallist=[{'id': 'Q3305213', 'text': 'painting'},
#                              {'id': 'Q860861', 'text': 'sculpture'}])
#            ## collection
#            print('''What is the object's collection?''')
#            pages[i]['collection'] = collect_data.match_wd_item('en',
#                proposallist=[{'id': 'Q812285', 'text':
#                               'Bavarian State Painting Collections'}])

            uniteddict = collect_data.unite(pages[i])
            augmenteddictlist.append(uniteddict)
            qsstring += collect_data.artworkjson2qs(uniteddict) + '\n'

            i += 1

#        # TODO: GET COLLECTION SOMEWHERE!!!!!!!
#        print('What does the object depict?') # TODO: other values here?
#        BETTER INTEGRATE THIS ADDITION FUNCITONALITY INTO collect_data.unite!

    return pages, augmenteddictlist, qsstring
    # TODO: currently no difference between pages and augmenteddictlist

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catname')
    args = parser.parse_args()

    # Renew Wikidata items TODO: this does not work! why?
    get_wd_bstgs.get_wd_bstgs()

    # Fetch data from the Commons category and integrate it
    dictlist, augmenteddictlist, qsstring = invnos_for_cat(args.catname)

    # Write write the JSON, the augmented JSON and QuickStatements
    # results to files
    filenametrunk = 'data/objects-' + args.catname
    collect_data.try_write_file(filenametrunk + '.json', json.dumps(dictlist,
        ensure_ascii=False, indent=4, sort_keys=True))
    collect_data.try_write_file(filenametrunk + '_plus.json', json.dumps(
        augmenteddictlist, ensure_ascii=False, indent=4, sort_keys=True))
    collect_data.try_write_file(filenametrunk + '_qs.txt', qsstring)


