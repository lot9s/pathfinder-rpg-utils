#!/usr/bin/python
#
#   The purpose of this script is to construct a database of Pathfinder RPG creatures by crawling
#   the d20pfsrd.
#

from lxml.html import parse

class PFCreatureInfo:
    '''Data structure representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
        
    def update_name_and_cr(self, doc):
        '''
        Updates the name and CR of creature from provided DOM object.
        '''
        top_bar = doc.cssselect('.sites-layout-tile th')
        if not top_bar:
            top_bar = doc.cssselect('.sites-layout-tile td')
            
        self.name = top_bar[0].text
        self.cr = top_bar[1].text
        
    def update(self, page):
        '''Update data structure with data found on the provided page.'''
        try:
            parsed_html = parse(page)
            doc = parsed_html.getroot()
    
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(doc)
            
            print self.cr, self.name

        except IOError:
            return None

def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the given page'''
    parsed_html = parse(page)
    doc = parsed_html.getroot()
    elements = doc.cssselect('div a')
    
    links = []
    for element in elements:
        link = element.get('href')
        if (link != None and 
            "monster-listings/" in link and
            not "-TOHC" in link and
            not "-tohc" in link):           
            links.append(link)
    return links
    
def get_html_indeces():
    '''Obtains the list of links to pages of creatures clustered by Challenge Rating.'''
    file = open('indeces.txt', 'r')
    indeces = file.readlines()
    for i in range(len(indeces)):
        indeces[i] = indeces[i].rstrip()
    return indeces

# script 
if __name__ == '__main__':
    indeces = get_html_indeces()
    
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        print link
        PFCreatureInfo().update(link)