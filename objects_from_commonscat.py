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
        'ext_image_data': '1', 'file_usage_data': '1', 'format': 'csv',
        'doit': '1'})
    url = ('http://tools.wmflabs.org/catscan3/catscan2.php?' + params)
    f = urllib.request.urlopen(url)

    newlines = f.read().decode('utf-8')
    newlines = newlines.split('\n')[1:]
    newlines = '\n'.join(newlines)
    newlines = io.StringIO(newlines)
    
    reader = csv.DictReader(newlines)
    pages = []
    for row in reader:
	    pages += [{'image': row['title'], 'nstext': row['nstext']}]
        # TODO: differentiate between image and commonscat!
        # take care of the spaces in commonscat!
        # row['nstext']
    return pages

def invnos_for_cat(catname):
    """Collect pages from a Wikimedia Commons Category, let the user \
    look for corresponding inventory numbers and return a dictionary \
    with the pairs.
    """
    pages = catpages(catname)
    i = 0
    while i < len(pages):
        params = urllib.parse.urlencode({'action': 'raw',
                                         'title': pages[i]['image']})
        url = 'https://commons.wikimedia.org/w/index.php?' + params
        print(url) # TODO: testing
        f = urllib.request.urlopen(url)
        f = f.read().decode('utf-8')
        print('\n', pages[i]['image'], '\n', f)
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
                        ': \n1 ' + pages[j]['image'] + '\n2 ' +
                        pages[i]['image'] + '.\nPlease enter the number of '
                        'the preferred one!\n')) - 1
                    pages[j]['image'] = [pages[j],pages[i]][selection]['image']
                    del pages[i]
        # Simply add the inventory number
        else:
            pages[i]['invno'] = answer
            i += 1

        # Differentiate between image and commonscat
        print(pages[i]['nstext']) # TODO: testing
        if pages[i]['nstext'] == 'Category':
            pages[i]['commonscat'] = pages[i]['image']
            del pages[i]['image']


#        # Add instanceOf, depicts etc. # TODO: better Commons parsing
#        ## instanceOf
#        print('What is the object instance of?')
#        pages[i]['instanceOf'] = collect_data.try_matching_str_to_wd(None,
#            'en', 'data/object_classes_mapping.json')
#        # TODO: make mapping file static?
#        print('What does the object depict?')
#        pages[i]['instanceOf'] = collect_data.try_matching_str_to_wd(None,
#            'en', None) # TODO: make mapping file optional!
#        # TODO: more
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




