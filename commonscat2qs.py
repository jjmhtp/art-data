#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import get_wd_bstgs
import objects_from_commonscat_2_with_json
import collect_data

parser = argparse.ArgumentParser()
parser.add_argument('catname')
args = parser.parse_args()

# Renew Wikidata items
get_wd_bstgs.get_wd_bstgs

# Run modules
itemdictlist = objects_from_commonscat_2_with_json.invnos_for_cat(args.catname)

collect_data.process_multiple(itemdictlist, inputname='data/objects-'+args.catname)


