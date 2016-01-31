'''A module containing functions and classes that allow one to scrape specific information from the Bestiary pages of d20pfsrd.com'''


from lxml.html import parse
from core.creature import Creature


# --- Constants ---
PROBLEM_LINKS = ['corgi-dire', 'darkwood-cobra', 'demodand-shaggy', 'demodand-slimy', 'demodand-tarry', 'demon-kalavakus', 'gashadokuru', 'great-white-shark', 'mimic-failed-apotheosis', 'mithral-cobra', 'mold-russet', 'protean-keketar', 'sinspawn-hub', 'sites.google.com', 'templates', 'TOC-']

PROBLEM_SUFFIXES = ['-TOHC', '-tohc', '-3PP', '-ff', '-kp', '-mb', '/beheaded', '/rakshasa']

THIRD_PARTY_PUBLISHERS = ['4 Winds Fantasy Gaming', 'Alluria Publishing', 'Frog God Games', 'Green Ronin Publishing', 'Jon Brazer Enterprises', 'Mystic Eye Games', 'Necromancer Games', 'Open Design LLC', 'Paizo Fans United', 'Super Genius Games', 'The Way of the Samurai', 'Tricky Owlbear Publishing']


# --- Functions ---
def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the given page'''
    parsed_html = parse(page)
    
    root = parsed_html.getroot()
    elements = root.cssselect('div a')
    
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
    '''
    Determines whether or not the provided link is a "problem" link. In this context, a 
    "problem" link is defined as one that leads to a non-creature entry or 3rd-party
    content. 
    '''
    # check if link is on list of problematic links
    for problem_link in PROBLEM_LINKS:
        if problem_link in link:
            return True
    #check if link has a suffix on list of problematic suffixes
    for suffix in PROBLEM_SUFFIXES:
        if link[-1 * len(suffix):] == suffix:
            return True
    return False
    
def is_problem_page(root):
    '''
    Determines whether or not the provided web page is a "problem" page. In this context,
    a "problm" page is defined as one that does not contain a 3rd-party creature.
    '''
    # check if publisher is a 3rd-party publisher
    #text_boxes = root.cssselect('.sites-embed-content-textbox')
    footers = root.cssselect('.sites-tile-name-footer')
    if footers:
        for footer in footers:
            footer_text = footer.text_content()
            if u'\xc2' in footer_text or '(c)' in footer_text or 'Copyright' in footer_text:
                for publisher in THIRD_PARTY_PUBLISHERS:
                    if publisher in footer_text:
                        return True
    # check if title indicates that the creature has 3rd-party affiliation
    title_element = root.cssselect('title')
    title = title_element[0].text
    if '3pp' in title:
        return True
    return False
        
    
# -- Script --- 
if __name__ == '__main__':
    indeces = get_html_indeces()
    # scrape d20pfsrd for creature info
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        print link
        parsed_html = parse(link)
        root = parsed_html.getroot()
        if not is_problem_page(root):
            Creature().update(root)
