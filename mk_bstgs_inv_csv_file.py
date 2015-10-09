#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Be careful! This script requires to run pdftotext in the shell.
# It is tested with pdftotext version 0.26.5.
# TODO:
# * test somewhere for the number of fields!

import urllib.request, urllib.error
import datetime
import subprocess
import re

def mk_inv_part_txt_file(filename):
    """This function downloads the inventory pdf file given by 'part' and
    saves it in the 'data' directory.
    It also saves the retrieval time of the file.
    It produces a txt file for the pdf file with pdftotext.
    """
    url = ('http://www.pinakothek.de/sites/default/files/files/' + filename)
    print(url)
#    RequestObj = urllib.request.urlopen(url)
    now = datetime.datetime.utcnow().isoformat()
    print(now)
#    RequestObjRead = RequestObj.read()
#    with open('data/' + filename, 'w+b') as pdffile:
#        pdffile.write(RequestObjRead)
    txtoutput = subprocess.check_output(['pdftotext', '-layout',
                                         'data/' + filename, '-'])
    # With PyPDF2 I got only blank lines ...
    txtoutput = txtoutput.decode('utf-8')
    return url, now, txtoutput

def process_bstgs_txt(txtinput):
    """This function processes the txt file returned by mk_inv_part_txt_file
    and returns a csv string with ordered content.
    """
    # TODO: It could be an alternative to read the fields and leave a rest
    #       instead of processing the lines
    betterOutput = txtinput
    # Remove lines without inventory object information
    ## Remove the text
    betterOutput = re.sub(r'BStGS {1,5}[AFKS]-[EJRZ]', r'', betterOutput)
    betterOutput = re.sub((r'Bestandsliste der Bayerischen '
                          r'Staatsgemäldesammlungen [AFKS]-[EJRZ]'), r'',
                          betterOutput)
    betterOutput = re.sub(r'Seite\s*[1-9][0-9]*', r'', betterOutput)
    ## Remove the whitespace
    betterOutput = re.sub(r'^\s*', r'', betterOutput, flags=re.M)
    # Remove all newlines breaking the information for one inventory object
    betterOutputList = betterOutput.split('\n')
    for i in range(len(betterOutputList)):
        if re.fullmatch(r'^([A-Z]{1,4}( [A-Z]{1,2})? {1,3}|Samz )?[0-9]' +
             r'{1,5}([^.,()0-9][^,()]*(\([^,()]*\)[^,()]*)?)?, .*$',
             betterOutputList[i]):
            betterOutputList[i] = '\n' + betterOutputList[i].strip()
        else:
            betterOutputList[i] = ' ' + betterOutputList[i].strip()
            # FIXME: incorrect handling of hyphens
    betterOutput = ''.join(betterOutputList)[1:] # without starting '\n'
    # Convert the object strings to object lists
    ## Escape "double quotes"
    ## FIXME: does this produce those strange double double quotes?
    betterOutput = re.sub(r'"', r'""', betterOutput)
    ## Quote some artists
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>'
        ### Comma after regional creation indication
        ### (The regex was created through the script mkArtistsToQuote.sh.)
        r'(Allgäuer|Augsburger|Deutsch|Flämisch|Italienisch|'
        r'Kölnisch|Oberitalienisch|Oberitalienisch\(\?\)|Schwäbisch|'
        r'Süddeutsch|Venezianisch|Westfälisch)( [^,]+)?, ([^,]*[0-9][^,]*'
        r'(Jh\.|Jahrhundert)[^,]*|(um |von )?[0-9]{4}|nach [A-Za-z]+ '
        r'Vorbild|1663\))'
        r'|'
        ### Comma before "gen." or "genannt"
        r'[^,]+, (gen.|genannt) [^,]+'
        r'|'
        ### Comma inside brackets
        r'[^,()]*\([^(),]*,[^()]*\)[^,()]*'
        r')'
        r', (?P<title>.*)$'),
        r'\g<invno>, "\g<artist>", \g<title>', betterOutput, flags=re.M)
    ## Quote titles with comma or excaped doublequote inside
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>[^,"][^,]+|"([^"]|"")+"), (?P<title>[^,\n]+,.*|.*"".*)$'),
        r'\g<invno>, \g<artist>, "\g<title>"', betterOutput, flags=re.M)
    # Return
    return betterOutput

def process_bstgs_txt2(txtinput):
    """This function processes the txt file returned by mk_inv_part_txt_file
    and returns a dictionary with ordered content.
    """ # TODO: dictionary?
    txtlines = txtinput.split('\n')
    txtlines2 = []
    for line in txtlines:
        if re.search((r'BStGS {1,5}[AFKS]-[EJRZ]|Bestandsliste der Bayerischen'
    print('Hello World!')
             r' Staatsgemäldesammlungen [AFKS]-[EJRZ]'), line) == None:
            txtlines2.append(line)
    print('txtlines is:', txtlines[:5])
    print('txtlines2 is:', txtlines2[:5])
    pagelines = ''
    for line in txtlines2:
        if re.search(r'Seite\s*[1-9][0-9]*', line) == None:
            pagelines += line
    print('pagelines is:', pagelines[:5])

    betterOutput = txtinput
    # Remove lines without inventory object information
    ## Remove the text
    betterOutput = re.sub(r'BStGS {1,5}[AFKS]-[EJRZ]', r'', betterOutput)
    betterOutput = re.sub((r'Bestandsliste der Bayerischen '
                          r'Staatsgemäldesammlungen [AFKS]-[EJRZ]'), r'',
                          betterOutput)
    betterOutput = re.sub(r'Seite\s*[1-9][0-9]*', r'', betterOutput)
    ## Remove the whitespace
    betterOutput = re.sub(r'^\s*', r'', betterOutput, flags=re.M)
    # Remove all newlines breaking the information for one inventory object
    betterOutputList = betterOutput.split('\n')
    for i in range(len(betterOutputList)):
        if re.fullmatch(r'^([A-Z]{1,4}( [A-Z]{1,2})? {1,3}|Samz )?[0-9]' +
             r'{1,5}([^.,()0-9][^,()]*(\([^,()]*\)[^,()]*)?)?, .*$',
             betterOutputList[i]):
            betterOutputList[i] = '\n' + betterOutputList[i].strip()
        else:
            betterOutputList[i] = ' ' + betterOutputList[i].strip()
            # FIXME: incorrect handling of hyphens
    betterOutput = ''.join(betterOutputList)[1:] # without starting '\n'
    # Convert the object strings to object lists
    ## Escape "double quotes"
    ## FIXME: does this produce those strange double double quotes?
    betterOutput = re.sub(r'"', r'""', betterOutput)
    ## Quote some artists
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>'
        ### Comma after regional creation indication
        ### (The regex was created through the script mkArtistsToQuote.sh.)
        r'(Allgäuer|Augsburger|Deutsch|Flämisch|Italienisch|'
        r'Kölnisch|Oberitalienisch|Oberitalienisch\(\?\)|Schwäbisch|'
        r'Süddeutsch|Venezianisch|Westfälisch)( [^,]+)?, ([^,]*[0-9][^,]*'
        r'(Jh\.|Jahrhundert)[^,]*|(um |von )?[0-9]{4}|nach [A-Za-z]+ '
        r'Vorbild|1663\))'
        r'|'
        ### Comma before "gen." or "genannt"
        r'[^,]+, (gen.|genannt) [^,]+'
        r'|'
        ### Comma inside brackets
        r'[^,()]*\([^(),]*,[^()]*\)[^,()]*'
        r')'
        r', (?P<title>.*)$'),
        r'\g<invno>, "\g<artist>", \g<title>', betterOutput, flags=re.M)
    ## Quote titles with comma or excaped doublequote inside
    betterOutput = re.sub((r'^(?P<invno>[^,]+), '
        r'(?P<artist>[^,"][^,]+|"([^"]|"")+"), (?P<title>[^,\n]+,.*|.*"".*)$'),
        r'\g<invno>, \g<artist>, "\g<title>"', betterOutput, flags=re.M)
    # Return
    return betterOutput

inv_parts = ['BStGS_A-E(2)', 'BStGS_F-J(2)', 'BStGS_K-R(2)', 'BStGS_S-Z(2)']


outputStr = ''
for part in inv_parts:
    url, now, txtoutput = mk_inv_part_txt_file(part + '.pdf')
#    text = process_bstgs_txt(txtoutput)
    print('txtoutput is:', txtoutput[:50]) # delete
    text = process_bstgs_txt2(str(txtoutput))
    text2 = ''
    for row in text.split('\n'):
        text2 += row + ',' + url + ',' + now + '\n'
    outputStr += text2

# Save the inventory comma separated values file
with open('data/bstgs_inventory.csv', 'w') as csvfile:
    csvfile.write(outputStr)



# Remove pointless whitespace # TODO: order not yet clear



