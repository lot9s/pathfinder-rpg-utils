'''A module containing functions that allow one to scrape data from the Bestiary pages of d20pfsrd.com and place it in a database'''


from lxml.html import parse
from core.creature import Creature

import sqlite3


# --- Constants ---
# the maximum number of retries allowed when attempting to download a web page
MAX_ATTEMPTS = 3

PROBLEM_LINKS = ['corgi-dire', 'darkwood-cobra', 'demodand-shaggy', 'demodand-slimy', 'demodand-tarry', 'demon-kalavakus', 'dlurgraven', 'dretch', 'formian-hive-queen', 'gashadokuru', 'great-white-shark', 'lemure', 'mimic-failed-apotheosis', 'mithral-cobra', 'mold-russet', 'protean-keketar', 'sinspawn-hub', 'sites.google.com', 'templates', 'TOC-']

PROBLEM_SUFFIXES = ['-TOHC', '-tohc', '-3PP', '-ff', '-kp', '-mb', '/beheaded', '/rakshasa']

THIRD_PARTY_PUBLISHERS = ['4 Winds Fantasy Gaming', 'Alluria Publishing', 'Frog God Games', 'Green Ronin Publishing', 'Jon Brazer Enterprises', 'Mystic Eye Games', 'Necromancer Games', 'Open Design LLC', 'Paizo Fans United', 'Super Genius Games', 'The Way of the Samurai', 'Tricky Owlbear Publishing']


# --- Functions ---
def clean_up(connection):
    '''
    Cleans up any initialized state in this script that may need it (i.e. Connection objects, etc.)
    
    :param connection: an open Connection object to a sqlite3 database
    '''
    connection.commit()
    connection.close()

def get_creature_links(page):
    '''
    Obtains the list of links to all non-3rd party creatures on the given page
    
    :param page: a string containing the complete link to a Bestiary page on d20pfsrd.com
    :returns: the list of links to all non-3rd party creatures on the given page
    '''
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
    
    :param link: a string containing the complete link to a Bestiary page on d20pfsrd.com
    :returns: True if the link is a problem link, False otherwise
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
    
    :param root: the root HtmlElement node of a Bestiary page from d20pfsrd.com
    :returns: True if the page is a problem page, False otherwise
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
    if title and '3pp' in title:
        return True
    return False

def open_database(name = 'creature.db'):
    '''
    Creates a connection to a sqlite3 database for storing Pathfinder RPG creature data. 
    If such a database does not yet exist, one is created.
    
    :param name: the name of the database; by default, this is creature.db
    :returns: a Connection object to the open sqlite3 database
    '''
    connection = sqlite3.connect(name)
    connection.text_factory = str
    return connection

    
# --- Script --- 
# By default, if this module is executed as a script, it will try to build a database of
# non-3rd party Pathfinder creatures by scraping creature data from d20pfsrd.com
if __name__ == '__main__':
    # open connection to sqlite3 database
    sql_conn = open_database()
    
    # get contents of file containing indeces to Pathfinder RPG creature pages
    indeces = get_html_indeces()
    
    # iterate over each obtained index
    for index in indeces:
        links = get_creature_links(index)
        # iterate over each link of the current index
        for link in links:
            # attempt to download the link we are interested in
            for i in range(MAX_ATTEMPTS):
                try:
                    parsed_html = parse(link)
                    root = parsed_html.getroot()
                    if not is_problem_page(root):
                        Creature().update(root)
                # if I/O exception raised, try again
                except IOError:
                    continue
                # if successful, break out of loop
                else:
                    break
            # if not successful, exit cleanly
            else:
                print 'ERROR: failed to download', link, 'after', MAX_ATTEMPTS, 'attempts.'
                clean_up(sql_conn)
                quit()
                
    # clean up
    clean_up(sql_conn)
