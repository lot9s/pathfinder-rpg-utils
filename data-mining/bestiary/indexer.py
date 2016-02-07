'''
This module contains a script and functions for obtaining a list of URLs from 
d20pfsrd.com, an unofficial System Reference Document (SRD) for the Pathfinder RPG. 

This list is meant to act as an index of creatures sorted by Challenge Rating (CR).
'''


from lxml.html import parse


# --- Constants ---
BASE_HREF = "http://www.d20pfsrd.com/"
CREATURE_BY_CR_URL = "http://www.d20pfsrd.com/bestiary/-bestiary-by-challenge-rating"


# --- Functions ---
def create_index_file(file_name='INDEX.txt'):
    '''
    Creates an index of links to d20pfsrd.com pages that contain links to Creature
    pages sorted by Challenge Rating (CR).
    
    :param file_name: the name of the output file
    '''
    out = open(file_name, 'w')
    
    # get root element of d20pfsrd's 'Creatures by CR' page
    html_tree = parse(CREATURE_BY_CR_URL)
    doc = html_tree.getroot()
    
    # write links to output file
    links = doc.cssselect('.nav-toc-content ul li a')
    for link in links:
        out.write(BASE_HREF + link.get('href') + '\n')
        
    # clean up
    out.close()
   
    
def create_special_index_file(file_name='INDEX_SPECIAL.txt'):
    '''
    Creates an index of links to Creature pages on d20pfsrd.com that are not
    obtainable by crawling the index file produced by create_index_file(...)
    without special treatment.
    
    :param file_name: the name of the output file
    '''
    # open input files
    hub_file = open('LINKS_SPECIAL_HUB.txt', 'r')
    links_file = open('LINKS_SPECIAL.txt', 'r')

    # open output files
    out = open(file_name, 'w')
    
    # get links from hub pages
    for line in hub_file:
        html_tree = parse(line.strip())
        doc = html_tree.getroot()
        link_table = doc.cssselect('.sites-tile-name-content-1 td:nth-child(1) a')
        # write links to output file
        for link in link_table:
            out.write(link.get('href') + '\n')
    
    # get links from special pages
    for line in links_file:
        out.write(line)
    
    # clean up
    hub_file.close()
    links_file.close()
    out.close()


# --- Script ---
if __name__ == '__main__':
    create_index_file()
    create_special_index_file()
    