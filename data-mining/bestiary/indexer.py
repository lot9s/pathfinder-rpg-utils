#!/usr/bin/python
#
#   This purpose of this script is to create a file containing an index of links to be used by
#   other scripts.
#
#   More specifically, these links are absolute HTML paths to pages on the d20pfsrd that list 
#   monster information from the Pathfinder RPG sorted by Challenge Rating.
#

from lxml.html import parse

BASE_HREF = "http://www.d20pfsrd.com/"
CREATURE_BY_CR_URL = "http://www.d20pfsrd.com/bestiary/-bestiary-by-challenge-rating"

if __name__ == '__main__':
    out = open('indeces.txt', 'w')
    
    parsed_html = parse(CREATURE_BY_CR_URL)
    
    doc = parsed_html.getroot()
    links = doc.cssselect('.nav-toc-content ul li a')
    
    for link in links:
        out.write(BASE_HREF + link.get('href') + '\n')
    out.close()