* refactoring for BStGS independence
* Template:Artwork parsing
* use pywikibot

# move through Commons files and cats
* all files and cats under cat
  -> need templates
* all of those with Template:Artwork or Category:Template:artwork possible or Template:Category definition: Object
  -> should get items on Wikidata
* all of those on Wikidata which are not linked by one of the items with inventory number and image

# old stuff
- improve documentation
    - [ ] write function docstrings
- convert_bstgs_inv.py
    - [ ] parse "d.Ä." etc correctly
    - [ ] parse "und" in artist fiels correctly
    - [ ] parse artwork groups in the title fields: [group[, partition]: ]part title (sometimes left out)
- pdf-conversion
    - [ ] handle the weird comma in the text for Bruyn and a problem with Inv. No. 6408
    - [ ] rewrite to use python
- [ ] get input data from Wikimedia Commons:
    - [ ] add inv. nos. to Commons file descriptions or rather collect it in a csv file
        - [ ] [https://commons.wikimedia.org/wiki/Category:Sculptures_in_the_Neue_Pinakothek](c:Category:Sculptures in the Neue Pinakothek) should be a good begin
- collection of inconsistencies in the BStGS inventory PDF files:
    - creator: "Honthorst-Nachahmer"
    - 'Olaf Gulbransson' sometimes not inverted
