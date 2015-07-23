#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Be careful! This script requires to run pdftotext in the shell.
# It is texte with pdftotext version 0.26.5.
# TODO:
# * test somewhere for the number of fields!

import urllib.request, urllib.error
import datetime
import subprocess
import re

def mk_inv_part_txt_file(part):
    """This function downloads the inventory pdf file given by 'part' and
    saves it in the 'data' directory.
    It also saves the retrieval time of the file.
    It produces a txt file for the pdf file with pdftotext."""
    url = ('http://www.pinakothek.de/sites/default/files/files/' + part)
    print(url)
    RequestObj = urllib.request.urlopen(url)
    # TODO: get the non-local retrieval time or date!
    now = datetime.datetime.now().isoformat()
    print(now)
    RequestObjRead = RequestObj.read()
    with open('data/' + part, 'w+b') as pdffile:
        pdffile.write(RequestObjRead)
    subprocess.call(['pdftotext', '-layout', 'data/' + part])
    # With PyPDF2 I got only blank lines ...

def process_txt_file(path):
    """This function processes the txt file returned by mk_inv_part_txt_file
    and returns a csv string with ordered content."""
    txtfile = open(path, 'r')
    messyInput = txtfile.read()
    betterOutput = messyInput
    txtfile.close()
    # Remove lines without inventory object information
    betterOutput = re.sub(r'\s*Seite\s*[1-9][0-9]*', r'', betterOutput)
    betterOutput = re.sub(r'\s*BStGS {1,5}[AFKS]-[EJRZ]', r'', betterOutput)
    betterOutput = re.sub(r'Bestandsliste der Bayerischen ' +
                          r'Staatsgemäldesammlungen [AFKS]-[EJRZ]', r'',
                          betterOutput)
    # Remove all newlines breaking the information for one inventory object
    betterOutputList = betterOutput.split('\n')
    for i in range(len(betterOutputList)):
        if re.fullmatch(r'^([A-Z]{1,4}( [A-Z]{1,2})? {1,3}|Samz )?[0-9]' +
             r'{1,5}([^.,()0-9][^,()]*(\([^,()]*\)[^,()]*)?)?, .*$',
             betterOutputList[i]):
            betterOutputList[i] = '\n' + betterOutputList[i]
        else:
            betterOutputList[i] = ' ' + betterOutputList[i].strip()
    betterOutput = ''.join(betterOutputList)
    # Convert the object strings to object lists
    ## Mask "double quotes"
    ## FIXME: does this produce those strange double double quotes?
    betterOutput = re.sub(r'"', r'""', betterOutput)
    ## Quote artists with comma inside after regional creation
    ## (regex is result of mkArtistsToQuote.sh)
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>(Allgäuer|Augsburger|Deutsch|Flämisch|Italienisch|'
        r'Kölnisch|Oberitalienisch|Oberitalienisch\(\?\)|Schwäbisch|'
        r'Süddeutsch|Venezianisch|Westfälisch)( [^,]+)?, ([^,]*[0-9][^,]*'
        r'(Jh\.|Jahrhundert)[^,]*|(um |von )?[0-9]{4}|nach [A-Za-z]+ '
        r'Vorbild|1663\))), (?P<title>.*)$'),
        r'\g<invno>, "\g<artist>", \g<title>', betterOutput, flags=re.M)
    ## Quote artists with comma before "gen." or "genannt"
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>[^,]+, (gen.|genannt) [^,]+), (?P<title>.*)$'),
        r'\g<invno>, "\g<artist>", \g<title>', betterOutput, flags=re.M)
    ## Quote artists with brackets for the case that there is a comma inside
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>[^,()]*\([^(),]*,[^()]*\)[^,()]*), (?P<title>.*)$'),
        r'\g<invno>, "\g<artist>", \g<title>', betterOutput, flags=re.M)
    ## Quote titles with comma inside
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>[^,"][^,]+|"([^"]|"")+"), (?P<title>[^,\n]+,.*)$'),
        r'\g<invno>, \g<artist>, "\g<title>"', betterOutput, flags=re.M)
    # Remove pointless whitespace # TODO: order not yet clear
    # Save the inventory comma separated values file
    txtfile = open('data/BStGS(2)-better.txt', 'w')
    txtfile.write(betterOutput)
    txtfile.close()

process_txt_file('data/BStGS(2).txt') # for testing

inv_parts = ['BStGS_A-E(2)', 'BStGS_F-J(2)', 'BStGS_K-R(2)', 'BStGS_S-Z(2)']

for part in inv_parts:

    break # TODO: editing mode only

    mk_inv_part_txt_file(part + '.pdf')
    # save in variable: process_txt_file('data/' + part + '.txt')
# concatenate strings in variables


# old fragments:
# try first!!:      sts = call('pdf2txt.py' + '-o' + ' data/bstgs_inventory_ae.txt' + ' data/bstgs_inventory_ae.pdf')
# pdftotext -layout 'BStGS_A-E(2).pdf'

#    pdfReader = PyPDF2.PdfFileReader(pdffile)
#
#    pageObj = pdfReader.getPage(5)
#    textpage = pageObj.extractText()
#    print(pdfReader.getNumPages())


#    print(textpage)

#f = f.read().decode('utf-8')
#g = json.loads(f)



