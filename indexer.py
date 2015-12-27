#!/usr/bin/python

import urllib

CREATURE_BY_CR_URL = "http://www.d20pfsrd.com/bestiary/-bestiary-by-challenge-rating"

page_ref = urllib.urlopen(CREATURE_BY_CR_URL)
page_html = page_ref.read()