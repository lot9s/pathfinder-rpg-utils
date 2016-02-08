'''A module containing functions that allow one to scrape data from the Bestiary pages of d20pfsrd.com and place it in a database'''

from lxml.html import parse
from core.creature import Creature
from db.creatureDB import CreatureDB


__all__ = ['create_db_entry', 'get_creature_links', 'get_html_indeces', 'is_problem_link', 'is_problem_page']


# --- Constants ---
# the maximum number of retries allowed when attempting to download a web page
MAX_ATTEMPTS = 3

PROBLEM_LINKS = ['/chimera', '/corgi-dire', '/darkwood-cobra', '/demodand-shaggy', '/demodand-slimy', '/demodand-tarry', '/demon-kalavakus', '/dlurgraven', '/dretch', '/formian-hive-queen', '/gashadokuru', '/great-white-shark', '/lemure', '/mimic-failed-apotheosis', '/minotaur-elder', '/mithral-cobra', '/mold-russet', '/protean-keketar', '/protean-imentesh', '/sinspawn-hub', '/zombie-hill-giant', 'sites.google.com', 'templates', 'TOC-']

PROBLEM_SUFFIXES = ['-TOHC', '-tohc', '-3PP', '-ff', '-kp', '-mb', '/beheaded', '/rakshasa']

THIRD_PARTY_PUBLISHERS = ['4 Winds Fantasy Gaming', 'Alluria Publishing', 'Frog God Games', 'Green Ronin Publishing', 'Jon Brazer Enterprises', 'Mystic Eye Games', 'Necromancer Games', 'Open Design LLC', 'Paizo Fans United', 'Super Genius Games', 'The Way of the Samurai', 'Tricky Owlbear Publishing']


# --- Functions ---
def create_db_entry(db_conn, link):
    '''
    Attempts to create a row in a CreatureDB object using a link to a Creature page
    on d20pfsrd.com
    
    :param db_conn: an open Connection object to a CreatureDB
    :param link: a string containing a link to a non-3rd party creature on d20pfsrd.com
    '''
    for i in range(MAX_ATTEMPTS):
        try:
            html_tree = parse(link)
            root = html_tree.getroot()
            # if the link is acceptable, create a creature entry in our database
            if not is_problem_page(root):
                creature = Creature()
                creature.update(root)
                # create table for CR of this creature if none exists
                db_conn.create_table(creature.cr)
                db_conn.add_creature(creature)
        # if I/O exception raised, try again
        except IOError:
            continue
        # if successful, break out of loop
        else:
            break
    # if not successful, exit cleanly
    else:
        raise Exception('ERROR: failed to download', link, 'after', MAX_ATTEMPTS, 'attempts.')
    

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
    file = open('INDEX.txt', 'r')
    indeces = file.readlines()
    for i, item in enumerate(indeces):
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

    
# --- Script --- 
# By default, if this module is executed as a script, it will try to build a database of
# non-3rd party Pathfinder creatures by scraping creature data from d20pfsrd.com
if __name__ == '__main__':
    # open connection to sqlite3 database
    db_connection = CreatureDB()
    
    try:
        # create a creature database entry for each link reachable by our index
        indeces = get_html_indeces()
        for index in indeces:
            links = get_creature_links(index)
            # iterate over each link of the current index
            for creature_link in links:
                create_db_entry(db_connection, creature_link)
        # create a creature database entry for each link in the special index
        special_index_file = open('INDEX_SPECIAL.txt', 'r')
        for line in special_index_file:
            create_db_entry(db_connection, line.strip())
    except Exception as e:
        print e.args[0]
                
    # clean up
    db_connection.commit_and_close()
