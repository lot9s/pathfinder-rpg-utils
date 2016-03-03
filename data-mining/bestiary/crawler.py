'''A module containing functions that allow one to scrape data from
the Bestiary pages of d20pfsrd.com and place it in a database'''


import sys
import traceback

from lxml.html import parse
from core.creature import Creature
from core.builders.creature.d20pfsrd import build as d20_build
from core.builders.creature.dict import build as dict_build
from db.creatureDB import CreatureDB


__all__ = ['create_db_entries_from_csv', 'create_db_entry_from_link', 
           'get_creature_links', 'get_html_indeces', 'is_problem_link', 
           'is_problem_page']


# --- Constants ---
# The maximum number of retries allowed when attempting to download
# a web page
MAX_ATTEMPTS = 3

PROBLEM_LINKS = [
    '/corgi-dire', 'chupacabra-giant-winged', '/darkwood-cobra', 
    '/dlurgraven', '/formian-hive-queen', '/gashadokuru', '/golem-clay',
    '/golem-ice', '/minotaur-elder', '/mithral-cobra', '/mold-russet', 
    'platypus', 'shaitan', '/sinspawn-hub', '/zombie-hill-giant', 
    'sites.google.com', 'templates', 'TOC-'
]

PROBLEM_SUFFIXES = [
    '-TOHC', '-tohc', '-3PP', '-ff', '-kp', '-mb', '/beheaded', 
    '/rakshasa'
]

THIRD_PARTY_PUBLISHERS = [
    '4 Winds Fantasy Gaming', 'Alluria Publishing', 
    'Frog God Games', 'Green Ronin Publishing', 
    'Jon Brazer Enterprises', 'Mystic Eye Games', 
    'Necromancer Games', 'Open Design LLC', 'Paizo Fans United', 
    'Super Genius Games', 'The Way of the Samurai', 
    'Tricky Owlbear Publishing'
]


# --- Functions ---
def create_db_entries_from_csv(db_conn, file_name='CREATURES_SPECIAL.csv'):
    '''Creates a row in a CreatureDB object using a .csv file
    containing creature attributes as described in the documentation
    for this project.
    
    :param db_conn: an open Connection object to a CreatureDB
    :param file_name: name of .csv file containing creature data
    '''
    # get creature data from .csv file
    creature_keys = []
    creature_file = open(file_name, 'r')
    for next_line in creature_file:
        creature_features = next_line.strip().split(',')
        # skip first line
        if next_line.startswith('CR,'):
            creature_keys = creature_features
            continue
        # create Creature object
        creature_dict = dict(zip(creature_keys, creature_features))
        creature = dict_build(creature_dict)
        # add Creature object to database
        db_conn.add_creature(creature)
        
    # clean up
    creature_file.close()


def create_db_entry_from_link(db_conn, link):
    '''Attempts to create a row in a CreatureDB object using a link to a 
    Creature page on d20pfsrd.com
    
    :param db_conn: an open Connection object to a CreatureDB
    :param link: link to non-3rd party creature on d20pfsrd
    '''
    for i in range(MAX_ATTEMPTS):
        try:
            html_tree = parse(link)
            root = html_tree.getroot()
            # if the link is acceptable, create a creature entry in our database
            if not is_problem_page(root):
                creature = d20_build(root)
                db_conn.add_creature(creature)
        # if I/O exception raised, try again
        except IOError:
            continue
        # if successful, break out of loop
        else:
            break
    # if not successful, exit cleanly
    else:
        raise Exception('ERROR: failed to download', link)
        
        
def display_help_message():
    '''Displays help message corresponding to -h command line
    argument'''
    print '''\nUSAGE: python crawler.py [-Ch]
            
          -C    CR values stored as strings, not integers
          -h    display help message
          
          --cr-range=<min>-<max>
                sets the valid range of CR values from <min> to <max>
          '''


def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the
    given page
    
    :param page: link to Bestiary page on d20pfsrd
    :returns: list of links to all non-3rd party creatures on page
    '''
    parsed_html = parse(page)
    
    root = parsed_html.getroot()
    elements = root.cssselect('div a')
    
    creature_links = []
    for element in elements:
        link = element.get('href')
        if (link is not None and
                'monster-listings/' in link and not is_problem_link(link)):
            creature_links.append(link)
    return creature_links


def get_html_indeces():
    '''Obtains the list of links to pages of creatures clustered by 
    Challenge Rating (CR)
    '''
    index_file = open('INDEX.txt', 'r')
    creature_indeces = index_file.readlines()
    for i, item in enumerate(creature_indeces):
        creature_indeces[i] = creature_indeces[i].rstrip()
    return creature_indeces
    
    
def is_problem_link(link):
    '''Determines whether or not the provided link is a "problem" 
    link. In this context, a "problem" link is defined as one that
    leads to a non-creature entry or 3rd-party content.
    
    :param link: string containing link to Bestiary page on d20pfsrd
    :returns: True if the link is a "problem" link, False otherwise
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
    '''Determines whether or not the provided web page is a "problem"
    page. In this context, a "problm" page is defined as one that does
    not contain a 3rd-party creature.
    
    :param root: root HtmlElement of a Bestiary page from d20pfsrd.com
    :returns: True if the page is a problem page, False otherwise
    '''
    # check if publisher is a 3rd-party publisher
    #text_boxes = root.cssselect('.sites-embed-content-textbox')
    footers = root.cssselect('.sites-tile-name-footer')
    if footers:
        for footer in footers:
            footer_text = footer.text_content()
            if (u'\xc2' in footer_text or
                   '(c)' in footer_text or 'Copyright' in footer_text):
                for publisher in THIRD_PARTY_PUBLISHERS:
                    if publisher in footer_text:
                        return True
    # check if title indicates that creature has 3rd-party affiliation
    title_element = root.cssselect('title')
    title = title_element[0].text
    if title and '3pp' in title:
        return True
    return False

    
# --- Script --- 
# By default, if this module is executed as a script, it will try to
# build a database of non-3rd party Pathfinder creatures by scraping
# creature data from d20pfsrd.com
#
# The resulting database will be exported in both .db (SQLite 3) and 
# .csv formats.
if __name__ == '__main__':
    # default settings
    db_name = 'creature.db'
    cr_range = [0.0, float('inf')]
    cr_flag = False
    
    # handle command line arguments
    for arg in sys.argv:
        # ignore sys.argv[0]
        if arg == __file__:
            continue
        # set 'using_nominal_cr' flag
        if arg == '-C':
            cr_flag = True
        # display help message and quit
        if arg == '-h':
            display_help_message()
            db_connection.commit_and_close()
            quit()
        # set valid CR range
        if '--cr-range=' in arg:
            values = arg[arg.index('=') + 1 :]
            cr_range[0] = float(values[: values.index('-')])
            cr_range[1] = float(values[values.index('-') + 1 :])
    
    # open connection to sqlite3 database
    db_connection = CreatureDB(db_name, cr_flag)
    db_connection.min_cr = cr_range[0]
    db_connection.max_cr = cr_range[1]
    
    # add entries to creature db via links to pages on d20pfsrd.com
    try:
        # create creature db entry for each reachable link
        indeces = get_html_indeces()
        for index in indeces:
            links = get_creature_links(index)
            # iterate over each link of the current index
            for creature_link in links:
                create_db_entry_from_link(db_connection, creature_link)
        # create creature db entry for each link in special index
        special_index_file = open('INDEX_SPECIAL.txt', 'r')
        for line in special_index_file:
            create_db_entry_from_link(db_connection, line.strip())
    except Exception as e:
        traceback.print_exc()
    
    # add entries to creature database via .csv file
    create_db_entries_from_csv(db_connection)
                
    # clean up
    db_connection.export_as_csv()
    db_connection.commit_and_close()
