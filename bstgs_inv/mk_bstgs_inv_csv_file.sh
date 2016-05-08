#!/bin/bash

####### DOWNLOAD THE 4 INVENTORY PDF FILES AND CONVERT THEM TO 1 TEXT FILE #######

wget 'http://www.pinakothek.de/sites/default/files/files/BStGS_A-E(2).pdf' 'http://www.pinakothek.de/sites/default/files/files/BStGS_F-J(2).pdf' 'http://www.pinakothek.de/sites/default/files/files/BStGS_K-R(2).pdf' 'http://www.pinakothek.de/sites/default/files/files/BStGS_S-Z(2).pdf'
pdftotext -layout 'BStGS_A-E(2).pdf'
pdftotext -layout 'BStGS_F-J(2).pdf'
pdftotext -layout 'BStGS_K-R(2).pdf'
pdftotext -layout 'BStGS_S-Z(2).pdf'
# TODO: insert source and retrieval date information and then concatenate later!
cat BStGS*.txt > inv1.txt
rm BStGS*



####### REMOVE LINES WITHOUT INVENTORY OBJECT INFORMATION #######

cp inv1.txt inv2.txt

# print warn notice if there are lines starting with "§"
sed -n -r '/^§.*/p' inv2.txt > log2warnNotice.txt
sed -i -r '1q' log2warnNotice.txt
sed -i -r 's/^§.*/The following lines start with "§". Please check if the result file is messy!/' log2warnNotice.txt
sed -n -r '/^§.*/p' inv2.txt >> log2warnNotice.txt
cat log2warnNotice.txt
rm log2warnNotice.txt

# mark lines to be removed
sed -i -r 's/^(\s*Seite {1,5}[1-9][0-9]?)$/§\1/g
s/^(\f.*|\s*BStGS {1,5}[AFKS]-[EJRZ])$/§\1/g
s/^(Bestandsliste der Bayerischen Staatsgemäldesammlungen [AFKS]-[EJRZ])$/§\1/g' inv2.txt

# write lines to be removed to log
sed -n -r '/^§.*/p' inv2.txt > log2removedLines.txt

# remove lines to be removed
sed -i -r 's/^§.*//g' inv2.txt
sed -i -r '/^$/d' inv2.txt



####### REMOVE ALL NEWLINES BREAKING THE INFORMATION FOR ONE INVENTORY OBJECT #######
# expected pattern for complete lines:
# inv. no., artist(, artist),( title(, title)…) ==> inv. no. and sth with >=2commas

cp  inv2.txt inv3.txt

# insert a "§" at the begin of all lines
sed -r 's/^(.*)$/§\1/g' inv3.txt > inv4.csv
mv inv4.csv inv3.txt

# remove the "§" from all lines with the pattern or complete lines
sed -r 's/^§(([A-Z]{1,4}( [A-Z]{1,2})? {1,3}|Samz )?[0-9]{1,5}([^.,()0-9][^,()]*(\([^,()]*\)[^,()]*)?)?, .*)$/\1/g' inv3.txt > inv4.csv
mv inv4.csv inv3.txt

# print log file with all lines with newline to be removed
sed -nr '/^§.*/p' inv3.txt > log3newlinesToRemove.txt

# remove newlines: 1st run
sed -r ':a ; N ; $!ba ; s/^(.*)$\n§ ?(.*)$/\1 \2/Mg' inv3.txt > inv4.csv
mv inv4.csv inv3.txt

# remove newlines: 2nd run
sed -r ':a ; N ; $!ba ; s/^(.*)$\n§ ?(.*)$/\1 \2/Mg' inv3.txt > inv4.csv
mv inv4.csv inv3.txt

# collect problem cases
sed -r ':a ; N ; N ; s/^[^,]*,[^,]*,.*$\n[^,]*,[^,]*,.*$\n[^,]*,[^,]*,.*$//g ; /^$/d' inv3.txt > log3problemCases.txt



####### CONVERT THE TEXT FILE TO A COMMA SEPERATED VALUES FILE AND REMOVE POINTLESS WHITESPACE TODO: seperate this! #######

cp  inv3.txt inv4.csv

# mask "double quotes" FIXME: does this produce those strange double double quotes?
sed -ri 's/"/""/g' inv4.csv

# quote artists with comma inside after regional creation (regex is result of mkArtistsToQuote.sh)
sed -ri 's/^([^,]+), ((Allgäuer|Augsburger|Deutsch|Flämisch|Italienisch|Kölnisch|Oberitalienisch|Oberitalienisch\(\?\)|Schwäbisch|Süddeutsch|Venezianisch|Westfälisch)( [^,]+)?, ([^,]*[0-9][^,]*(Jh\.|Jahrhundert)[^,]*|(um |von )?[0-9]{4}|nach [A-Za-z]+ Vorbild|1663\))), (.*)$/\1, "\2", \8/g' inv4.csv

# quote artists with comma before "gen." or "genannt"
sed -ri 's/^([^,]+), ([^,]+, (gen.|genannt) [^,]+), (.*)$/\1, "\2", \4/g' inv4.csv

# quote artists with brackets for the case that there is a comma inside
sed -ri 's/^([^,]+), ([^,()]*\([^(),]*,[^()]*\)[^,()]*), (.*)$/\1, "\2", \3/g' inv4.csv

# quote titles with comma inside
sed -ri 's/^([^,]+, ([^,"][^,]+|"([^"]|"")+"), )([^,]+,.*)$/\1"\4"/g' inv4.csv

# print irregular lines notice TODO: not yet tested
echo "The following lines don't have exactly three fields:"
#sed -r 's/^(([^,"]|"")+|"([^"]|"")+"),(([^,"]|"")+|"([^"]|"")+"),(([^,"]|"")+|"([^"]|"")+")/§/g' inv4.csv | sed -nr '/(^[^§]|§.+)/p'

# trim whitespace at begin of title fields FIXME: seems not to be correct, no \4?
sed -ri 's/^([^,]+, ([^,"][^,]+|"([^"]|"")+"), "?)\s+(.*)$/\1\4/g' inv4.csv

# trim spaces between fields
sed -ri 's/^([^,]+), ([^,"][^,]+|"([^"]|"")+"), (.*)$/\1,\2,\4/g' inv4.csv

# write quoted artists to log file
sed -nr '/^[^,]+,"/p' inv4.csv | sed -r 's/^[^,]+,("[^"]+"),.*/\1/g' > log4quotedArtists.csv

# TODO: there is still pointless whitspace at the beginning of some artist fields, e.g. "    Deutsch"

####### STORE LOG FILES #######

mv log* data/logfiles/
mv inv[1-3].txt data/
mv inv4.csv data/bstgs_inventory.csv



####### TODO #######
# * perhaps make some normalization edits adapted to strange single solutions and then parse the rest with rules?
#
# outdated:
# * tweet to @Pinakotheken
# # check if al rows have 3 fields: sed -r 's/^(([^,"]|"")+|"([^"]|"")+"),(([^,"]|"")+|"([^"]|"")+"),(([^,"]|"")+|"([^"]|"")+")/foo/g' inv4.csv | sed -nr '/^[^f]/p'
# # remove messy whitespace from inv. no. and artist fields: all whitespace at begin and end; shrink several spaces to one
# # match with exitsing Wikidata items (easy)
# # match with Commons files without Wikidata items
#     # go over all files in the subcat without either [[Template:Artwork]] or [[Template:Object photo]] or [[Category:Template:Artwork possible]] and add [[Category:Template:Artwork possible]] (2014-10-04T13: 560): http://tools.wmflabs.org/catscan2/catscan2.php?language=commons&project=wikimedia&depth=15&categories=Bayerische+Staatsgem%C3%A4ldesammlungen&negcats=Template%3AArtwork+possible&ns%5B6%5D=1&templates_no=Artwork%0D%0AObject+photo&format=gallery&doit=1
#     # list files in the subcat with [[Category:Template:Artwork possible]] (2014-10-04T13: … TODO!
#     # list files in the subcat with either [[Template:Artwork]] or [[Template:Object photo]] (2014-10-04T13: 1694): http://tools.wmflabs.org/catscan2/catscan2.php?language=commons&project=wikimedia&depth=15&categories=Bayerische+Staatsgem%C3%A4ldesammlungen&ns%5B6%5D=1&templates_any=Artwork%0D%0AObject+photo&format=gallery&doit=1
#     # extract creator, title and accession number information for those files
#     # match manually with the existing inventory
# # match with pinakothek.de exhibition rooms, …
# # add items with images to Wikidata (& Commons)



