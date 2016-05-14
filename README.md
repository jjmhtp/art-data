# art-data
This repository holds scripts to collect data about artworks and to process it for adding it to Wikidata. The data is collected in the "data" directory. At the moment the project is focussed on the objects of the Bavarian State Paintings Collections (German: Bayerische Staatsgemäldesammlungen; BStGS). But I have to remove this dependency!

Currently the scripts do not use pywikibot but can output collected data in the input format for [QuickStatements](https://tools.wmflabs.org/wikidata-todo/quick_statements.php) though this has some restrictions.

Starting points are:
* `collect_data.py` which can take inventory numbers of the BStGS as an input. See `python3 collect_data.py --help` for more.
* `objects_from_commonscat.py` which takes which takes a Wikimedia Commons category as input, uses the files and subcategories to create starting items and can interactively enrich it with more data.
