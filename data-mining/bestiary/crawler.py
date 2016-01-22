'''A module containing functions and classes that allow one to scrape specific information from the Bestiary pages of d20pfsrd.com'''

from lxml.html import parse
import string


# --- Constants ---
PROBLEM_LINKS = ['corgi-dire', 'darkwood-cobra', 'sinspawn-hub', 'TOC-']
PROBLEM_SUFFIXES = ['-TOHC', '-tohc', '-3PP', '-ff', '-kp']


# --- Functions ---
def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the given page'''
    parsed_html = parse(page)
    doc = parsed_html.getroot()
    elements = doc.cssselect('div a')
    
    links = []
    for element in elements:
        link = element.get('href')
        if link != None and "monster-listings/" in link and not is_problem_link(link):           
            links.append(link)
    return links
    
def get_html_indeces():
    '''Obtains the list of links to pages of creatures clustered by Challenge Rating.'''
    file = open('indeces.txt', 'r')
    indeces = file.readlines()
    for i in range(len(indeces)):
        indeces[i] = indeces[i].rstrip()
    return indeces
    
def is_problem_link(link):
    '''Determines whether or not the provided link is a "problem" link. (i.e. link does not lead to a creature entry, etc.)'''
    # check if link is on list of problematic links
    for problem_link in PROBLEM_LINKS:
        if problem_link in link:
            return True
    #check if link has a suffix on list of problematic suffixes
    for suffix in PROBLEM_SUFFIXES:
        if link[-1 * len(suffix):] == suffix:
            return True
    return False


# --- Classes --- 
class PFCreatureInfo:
    '''Data structure representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
    
    def format_name(self, name):
        '''Returns copy of string argument with each word capitalized'''
        new_name = name.lower()
        # capitalize space-separated words
        new_name = string.capwords(new_name, ' ')
        # capitalize words following a hyphen
        index = new_name.find('-') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        # capitalize words following a left parenthesis
        index = new_name.find('(') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        return new_name
    
    def update_name_and_cr(self, doc):
        '''
        Updates the name and CR of creature from provided DOM object
        '''
        # <td> element contains Name and CR
        info_element = doc.cssselect('td.sites-layout-tile th')
        
        # <th> element contains Name and CR
        if not info_element:
            info_element = doc.cssselect('td.sites-layout-tile td')
        
        child_l = info_element[0]
        child_r = info_element[1]
        self.name = self.format_name(child_l.text_content().strip())
        self.cr = child_r.text_content().strip()
        
    def update(self, page):
        '''Updates data structure with data found on the provided page'''
        try:
            parsed_html = parse(page)
            doc = parsed_html.getroot()
    
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(doc)
            
            print self.cr, self.name
            print ''

        except IOError:
            return None


# script 
if __name__ == '__main__':
    indeces = get_html_indeces()
    
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        print link
        PFCreatureInfo().update(link)