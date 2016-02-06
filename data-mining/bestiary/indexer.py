'''A script that obtains a list of URLs from d20pfsrd.com, an unofficial System Reference Document (SRD) for the Pathfinder RPG. This list acts as an index of creatures sorted by Challenge Rating (CR).'''

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
    