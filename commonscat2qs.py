#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import get_wd_bstgs
import objects_from_commonscat
import collect_data

parser = argparse.ArgumentParser()
parser.add_argument('catname')
args = parser.parse_args()

# Renew resources (optionaly)
## Renew Wikidata items
get_wd_bstgs.get_wd_bstgs
## Renew BStGS inventory
# TODO

# Run modules
itemdictlist = objects_from_commonscat.invnos_for_cat(args.catname)

collect_data.process_multiple(itemdictlist, inputname='data/objects-'+args.catname)


