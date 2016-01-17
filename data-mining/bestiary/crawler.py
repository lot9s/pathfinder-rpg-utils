'''A module containing functions and classes that allow one to scrape specific information from the Bestiary pages of d20pfsrd.com'''

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
        top_bar = doc.cssselect('.sites-layout-tile th')            # try mining the table header
        if not top_bar:
            top_bar = doc.cssselect('.sites-layout-tile td')        # try mining the table entries
            if top_bar and \
               len(top_bar[0]) > 0 and \
               top_bar[0][0].tag == 'b':                            # check if table entries are <b>
                top_bar = [ top_bar[0][0], top_bar[1][0] ]
            
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
    
def is_3pp(link):
    '''Determines whether or not content from the given link is 3rd Party content or not.'''
    if "corgi-dire" in link or link[-3:] == "-kp" or link[-4:] == "-3PP":
        return True
    return False

# script 
if __name__ == '__main__':
    indeces = get_html_indeces()
    
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        if is_3pp(link):
            continue
        print link
        PFCreatureInfo().update(link)