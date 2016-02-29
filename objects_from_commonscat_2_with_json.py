#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import io
import csv
import json
import collect_data

def catpages(catname):
    params = urllib.parse.urlencode({'language': 'commons', 'project':
        'wikimedia', 'categories': catname, 'ns[6]': '1', 'ns[14]': '1',
        'ext_image_data': '0', 'file_usage_data': '0', 'format': 'json',
        'doit': '1'})
    url = ('http://tools.wmflabs.org/catscan3/catscan2.php?' + params)
    f = urllib.request.urlopen(url)

    pages = json.loads(f.read().decode('utf-8'))
    pages = pages['*'][0]['*']
    simplepages = []
    for page in pages:
        simplepages += [{'title': page['a']['title'].replace('_', ' '),
                         'nstext': page['a']['nstext']}]

    return simplepages

def invnos_for_cat(catname):
    """Collect pages from a Wikimedia Commons Category, let the user \
    look for corresponding inventory numbers and return a dictionary \
    with the pairs.
    """
    pages = catpages(catname)
    i = 0
    # Add inventory numbers
    while i < len(pages):
        params = urllib.parse.urlencode({'action': 'raw',
            'title': pages[i]['nstext'] + ':' + pages[i]['title']})
        url = 'https://commons.wikimedia.org/w/index.php?' + params
        f = urllib.request.urlopen(url)
        f = f.read().decode('utf-8')
        print('\n', pages[i]['nstext'] + ':' + pages[i]['title'],
              '\n', f)
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
                    selection = int(input('The following two images depict '
                        'the object with the inventory number ' + answer +
			': \n1 ' + pages[j]['nstext'] + ':' +
                        pages[j]['title'] + '\n2 ' + pages[i]['nstext'] +
                        ':' + pages[i]['title'] +
                        '.\nPlease enter the number of the preferred ' +
                        'one!\n')) - 1
                    # TODO: print also URLs here!
                    duplicates = [pages[j],pages[i]]
                    print('duplicates: ', duplicates)
                    pages[j]['nstext'] = duplicates[selection]['nstext']
                    pages[j]['title'] = duplicates[selection]['title']
         #           betterdup = duplicates.pop(selection)
         #           pages[i]['nstext'] = betterdup['nstext']
         #           pages[i]['title'] = betterdup['title']
         #           if 'notusedfiles' in pages[j].keys():
         #               pages[i]['notusedfiles'] += duplicates
         #           else:
         #               pages[i]['notusedfiles'] = duplicates
                    # TODO: improve evtl
                    print('i (eig neu): ', pages[i], '\nj (eig alt): ', pages[j])
                    del pages[j]
        # Simply add the inventory number
        else:
            pages[i]['invno'] = answer
            i += 1
            # Add instanceOf, depicts etc. # TODO: better Commons parsing
            ## instanceOf
            print('What is the object instance of?')
            pages[i]['instanceOf'] = collect_data.match_wd_item('en',
                mappingjsonfile='data/object_classes_mapping.json',
                proposallist=[{'id': 'Q3305213', 'text': 'painting'}])
            ## collection
            print('''What is the object's collection?''')
            pages[i]['collection'] = collect_data.match_wd_item('en',
                proposallist=[{'id': 'Q812285', 'text':
                               'Bavarian State Painting Collections'}])
    


#        # TODO: GET COLLECTION SOMEWHERE!!!!!!!
#        print('What does the object depict?') # TODO: other values here?

    # Compose dictionary with image and commonscat values
    for k in range(len(pages)):
        if pages[k]['nstext'] == 'File':
            pages[k]['image'] = pages[k]['title']
        elif pages[k]['nstext'] == 'Category':
            pages[k]['commonscat'] = pages[k]['title']
        del pages[k]['nstext']
        del pages[k]['title']

    return pages

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catname')
    args = parser.parse_args()

    result = invnos_for_cat(args.catname)

    print(result)

    with open('data/objects-' + args.catname + '.json', 'w') as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=4,
                                sort_keys=True))


