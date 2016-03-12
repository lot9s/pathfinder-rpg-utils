'''A module containing functions that allow one to scrape data from
the Bestiary pages of d20pfsrd.com and place it in a database'''


import argparse
import traceback

from lxml.html import parse
from core.builders.creature.d20pfsrd import build as d20_build
from core.builders.creature.dict import build as dict_build
from db.creatureDB import CreatureDB


__all__ = []


# --- Constants ---
# The maximum number of retries allowed when attempting to download
#   a web page
MAX_ATTEMPTS = 3

# TODO: Content Collection Modes
MODE_3PP = 1        # collect 3rd party content only
MODE_ALL = 2        # collect all content
MODE_STANDARD = 0   # collect non-3rd party content only

# Each of these lists is used to filter content scraped from the 
#   Bestiary pages of d20pfsrd.com depending on the Content Collection
#   Mode.
PROBLEM_LINKS = []
PROBLEM_SUFFIXES = []
THIRD_PARTY_PUBLISHERS = []
THIRD_PARTY_SUFFIXES = []


# --- Functions ---
def create_db_entries_from_csv(db_conn, file_name='CREATURES_SPECIAL.csv'):
    '''Creates a row in a CreatureDB object using a .csv file
    containing creature attributes as described in the documentation
    for this project
    
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


def create_db_entry_from_link(db_conn, link, mode=MODE_STANDARD):
    '''Attempts to create a row in a CreatureDB object using a link to a 
    Creature page on d20pfsrd.com
    
    :param db_conn: an open Connection object to a CreatureDB
    :param link: link to non-3rd party creature on d20pfsrd
    :param mode: the content collection mode set by the user
    '''
    for i in range(MAX_ATTEMPTS):
        try:
            html_tree = parse(link)
            root = html_tree.getroot()
            # if link is acceptable, create Creature entry in db
            if not is_problem_page(root, mode):
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


def get_creature_links(page, mode=MODE_STANDARD):
    '''Gets the list of links to all desired content on the given page
    
    :param page: link to Bestiary page on d20pfsrd
    :param mode: the content collection mode set by the user
    :returns: list of links to all desired content on page
    '''
    parsed_html = parse(page)
    
    root = parsed_html.getroot()
    elements = root.cssselect('div a')
    
    creature_links = []
    for element in elements:
        link = element.get('href')
        if (link is not None and 'monster-listings/' in link and 
              not is_problem_link(link, mode)):
            creature_links.append(link)
    return creature_links


def get_html_indeces():
    '''Gets the list of links to pages of creatures clustered by 
    Challenge Rating (CR)
    '''
    index_file = open('INDEX.txt', 'r')
    creature_indeces = index_file.readlines()
    for i, item in enumerate(creature_indeces):
        creature_indeces[i] = creature_indeces[i].rstrip()
    return creature_indeces


def is_3pp_link(link):
    '''Determines whether or not the provided link leads to 3rd party
    content
    
    :param link: string containing link to Bestiary page on d20pfsrd
    :returns: True if link leads to 3rd party content, False otherwise
    '''
    # check if link contains a suffix denoting its 3rd party status
    if link.endswith(tuple(THIRD_PARTY_SUFFIXES)):
        return True
    # check if page the link leads to contains 3rd party content
    html_tree = parse(link)
    root = html_tree.getroot()
    if is_3pp_page(root):
        return True
    return False


def is_3pp_page(root):
    '''Determines whether or not the given HtmlElement node contains
    3rd party content
    
    :param root: root HtmlElement of a Bestiary page from d20pfsrd.com
    :returns: True if page contains 3rd party content, False otherwise
    '''
    # check if publisher is a 3rd-party publisher
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


def is_problem_link(link, mode=MODE_STANDARD):
    '''Determines whether or not the provided link is a "problem" 
    link
    
    In this context, a "problem" link is defined as one that
    leads to undesirable content.
    
    :param link: string containing link to Bestiary page on d20pfsrd
    :param mode: the content collection mode set by the user
    :returns: True if the link is a "problem" link, False otherwise
    '''
    # check if link is on list of problematic links
    for problem_link in PROBLEM_LINKS:
        if problem_link in link:
            return True
    if link.endswith(tuple(PROBLEM_SUFFIXES)):
            return True
    # check if link contains 3rd party content
    is_3pp_link_ = is_3pp_link(link)
    if mode == MODE_STANDARD and is_3pp_link_:
        return True
    if mode == MODE_3PP and not is_3pp_link_:
        return True
    return False


def is_problem_page(root, mode=MODE_STANDARD):
    '''Determines whether or not the content in the provided HtmlElemnt
    node is desired
    
    :param root: root HtmlElement of a Bestiary page from d20pfsrd.com
    :param mode: the content collection mode set by the user
    :returns: True if content on page is not desired, False otherwise
    '''
    if mode == MODE_STANDARD:
        return is_3pp_page(root)
    if mode == MODE_3PP:
        return not is_3pp_page(root)
    return False


def load_list(file_name):
    '''Gets list of newline-separated strings from file
    
    :param file_name: file containing list of strings
    :returns list of strings
    '''
    file_ = open(file_name, 'r')
    list_ = file_.read().split('\n')
    file_.close()
    return list_


# --- Script --- 
# By default, if this module is executed as a script, it will try to
# build a database of non-3rd party Pathfinder creatures by scraping
# creature data from d20pfsrd.com
#
# The resulting database will be exported in both .db (SQLite 3) and 
# .csv formats.
if __name__ == '__main__':
    THIRD_PARTY_PUBLISHERS = load_list('3PP.txt')
    THIRD_PARTY_SUFFIXES = load_list('LINKS_3PP_SUFFIXES.txt')
    PROBLEM_LINKS = load_list('LINKS_PROBLEM.txt')
    PROBLEM_SUFFIXES = load_list('LINKS_PROBLEM_SUFFIXES.txt')
    
    # default settings
    db_name = 'creature.db'
    cr_range = [0.0, float('inf')]
    cr_flag = False
    content_mode = MODE_STANDARD
    
    # create parser for command line arguments
    parser = argparse.ArgumentParser(description='Builds a creature database')
    # -argument- challenge rating storage mode
    parser.add_argument('-C', action='store_true',
                        help='store CR values as strings, not integers')
    # -argument- range of accepted challenge rating values
    parser.add_argument('--cr-range', 
                        nargs=2, metavar=('MIN', 'MAX'), type=float,
                        help='sets valid range of CR values')
    # -argument- content collection mode
    content_mode_choices = ['standard', '3pp', 'all']
    parser.add_argument('--content',
                        nargs=1, choices=content_mode_choices,
                        help='sets type of creatures in db')
    # parse command line arguments
    args = vars(parser.parse_args())
    
    # handle command line arguments
    for key in args:
        if key == 'C':
            cr_flag = args['C']
        if key == 'cr_range' and args['cr_range']:
            cr_range = args['cr_range']
        if key == 'content' and args['content']:
            content_mode = content_mode_choices.index(args['content'][0])
    
    # create sqlite3 database
    db_connection = CreatureDB(db_name, cr_flag)
    db_connection.min_cr = cr_range[0]
    db_connection.max_cr = cr_range[1]
    
    # add entries to creature db via links to pages on d20pfsrd.com
    try:
        # create creature db entry for each reachable link
        indeces = get_html_indeces()
        for index in indeces:
            links = get_creature_links(index, content_mode)
            # iterate over each link of the current index
            for creature_link in links:
                create_db_entry_from_link(db_connection, creature_link, 
                                          content_mode)
        # create creature db entry for each link in special index
        special_index_file = open('INDEX_SPECIAL.txt', 'r')
        for line in special_index_file:
            create_db_entry_from_link(db_connection, line.strip(), content_mode)
    except Exception as e:
        traceback.print_exc()
    
    # add entries to creature database via .csv file
    if not content_mode == MODE_3PP:
        create_db_entries_from_csv(db_connection, 'CREATURES_SPECIAL.csv')
    if not content_mode == MODE_STANDARD:
        create_db_entries_from_csv(db_connection, '3PP_CREATURES_SPECIAL.csv')
                
    # clean up
    db_connection.export_as_csv()
    db_connection.commit_and_close()
