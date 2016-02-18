'''A module containing a class for representing and manipulating 
creature information from the Pathfinder RPG'''


import re
import string


__all__ = ['Creature']


# --- Constants ---
ABILITIES = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
ATTRIBUTES = ['DEFENSE', 'AC', 'touch', 'flat-footed', 'STATISTICS', 'Base']


# --- Functions ---
def check_text_for_spaces(text, keywords, start=0):
    '''
    Checks text for spaces before and after certain keywords. If a 
    space is not present, it gets inserted into the text in the 
    appropriate place.
    
    :param text: the text to be checked
    :param keywords: list of words required to have spaces follow them
    :param start: starting index in text to begin checking at
    :returns version of 'text' with spaces where they should be
    '''
    _text = text
    for word in keywords:
        indx = _text.find(word, start)
        # check for space after keyword
        if _text[indx + len(word)] != ' ':
            _text = insert_text(_text, indx + len(word), ' ')
        indx = _text.find(word, start)
        # check for space before keyword
        if _text[indx-1] != ' ':
            _text = insert_text(_text, indx, ' ')
    return _text


def format_creature_entry(entry):
    '''Returns copy of creature entry formatted such that it is easily 
    parsable
    
    :param entry: Creature entry scraped from d20pfsrd bestiary page
    :returns: a formatted copy of the Creature entry
    '''
    _entry = entry.encode('ascii', 'ignore') # remove unicode chars
    _entry = _entry.replace("*", "")      
    _entry = _entry.replace(",", ", ")    
    _entry = _entry.replace("flatfooted", "flat-footed")
    # add spaces where needed
    _entry = check_text_for_spaces(_entry, ATTRIBUTES)
    _entry = check_text_for_spaces(_entry, ABILITIES, _entry.find('STATISTICS'))
    # replace all occurrences of white space with a single ' '
    _entry = re.sub(r"\s+", ' ', _entry)
    return _entry


def format_creature_name(name):
    '''
    Returns copy of name argument formatted appropriately
    
    :param name: a string containing an unformatted Creature name
    :returns: a formatted Creature name
    '''
    new_name = name.encode('ascii', 'ignore')   # remove unicode chars
    new_name = new_name.lower()
    # capitalize space-separated words
    new_name = string.capwords(new_name, ' ')
    # capitalize words following a hyphen
    indx = new_name.find('-') + 1
    new_name = new_name[:indx] +  new_name[indx].upper() + new_name[indx+1:]
    # capitalize words following a left parenthesis
    indx = new_name.find('(') + 1
    new_name = new_name[:indx] +  new_name[indx].upper() + new_name[indx+1:]
    return new_name

    
def get_cr_and_mr_from_text(text):
    '''
    If present within the given text, returns a tuple containing a 
    creature's Challenge Rating (CR) and Mythic Rank (MR)
    
    It is expected that the given text will be of the form 'CR X/MR Y'
    
    :param text: a string containing an unformatted Creature CR
    :returns: a tuple of the form (CR, MR)
    '''
    cr_text = text
    creature_cr = '0'
    creature_mr = '0'
    # if not present, insert spaces where needed
    if not cr_text[:3] == 'CR ':
        cr_text = insert_text(cr_text, 2, ' ')
    # replace any occurrence of * with ''
    cr_text = cr_text.replace('*', '')
    
    # case 1: text contains mythic rank
    if 'MR' in cr_text:
        ranks = cr_text.split('/M')
        # get challenge rating
        cr_words = ranks[0].split(' ')
        creature_cr = cr_words[1]
        # get mythic rank
        mr_words = ranks[1].split(' ')
        creature_mr = mr_words[1]
    # case 2: text does not contain mythic rank
    else:
        cr_words = cr_text.split(' ')
        cr_text = cr_words[1]
        # handle Challenge Ratings with fractional values 
        if '/' in cr_text:
            cr_text = str(float(cr_text[0]) / float(cr_text[2]))
            # truncate strings with long floating point values
            if len(cr_text) > 4:
                cr_text = cr_text[:4]
        creature_cr = cr_text
    
    return (creature_cr, creature_mr)

  
def insert_text(orig_text, index, insert_text):
    '''Creates a new string by inserting one string into another at
    some specified index
    
    :param orig_text: the original string
    :param index: index of original string to insert text into
    :param insert_text: string that will be inserted into the original
    :returns the new string after the insertion
    '''
    return "%s%s%s" % (orig_text[:index], insert_text, orig_text[index:])


# --- Classes ---
class Creature(object):
    '''Class representing a creature from the Pathfinder RPG'''
    
    def __init__(self):
        self.name = ''
        self.cr = '0'
        self.mr = '0'
        self.ability_scores = {'Str': '0', 'Dex': '0', 'Con': '0', 
                               'Int': '0', 'Wis': '0', 'Cha': '0'}
        self.ac = {'AC': '0', 'touch': '0', 'flat-footed': '0'}
        
    def __repr__(self):
        values = [self.cr, self.name, '\n',
                  str(self.ability_scores), '\n', 
                  str(self.ac)]
        return ' '.join(values)
    
    def __str__(self):
        values = [self.cr, self.name, '\n',
                  'Str', self.ability_scores['Str'],
                  'Dex', self.ability_scores['Dex'],
                  'Con', self.ability_scores['Con'],
                  'Int', self.ability_scores['Int'],
                  'Wis', self.ability_scores['Wis'],
                  'Cha', self.ability_scores['Cha'], '\n',
                  'AC', self.ac['AC'],
                  'touch', self.ac['touch'],
                  'flat-footed', self.ac['flat-footed'], '\n\n']
        return ' '.join(values)
        
    def _update_abilities(self, words):
        '''Updates the Creature's ability score values using the 
        Creature's entry on d20pfsrd.com split into individual words
        
        :param words: text of d20pfsrd bestiary page as list of words
        '''
        for key in self.ability_scores.keys():
            index = words.index(key, words.index("STATISTICS"))
            parsed_ability = words[index+1]
            parsed_ability = parsed_ability.replace(",", "")
            parsed_ability = parsed_ability.replace(";", "")
            if parsed_ability == '' or '-' in parsed_ability:
                self.ability_scores[key] = '-1'
            else:
                self.ability_scores[key] = parsed_ability
        
    def _update_ac(self, words):
        '''Updates the Creature's armor class values using the 
        Creature's entry on d20pfsrd.com split into individual words
        
        :param words: text of d20pfsrd bestiary page as list of words
        '''
        for key in self.ac.keys():
            index = words.index(key, words.index("AC"))
            parsed_ac = words[index+1]
            parsed_ac = parsed_ac.replace(",", "")
            parsed_ac = parsed_ac.replace(";", "")
            self.ac[key] = parsed_ac
        
    def _update_entry_values(self, root):
        '''Updates the values for this Creature that are normally found 
        in the main section of a Monster entry
        
        This is done using data in root of HtmlElement tree 
        corresponding to the Creature's page on d20pfsrd.com
        
        :param root: root element of an HtmlElement tree
        '''
        # get the page's creature text
        content = root.cssselect('.sites-canvas-main')
        content_element = content[0]
        content_text = content_element.text_content()
        # format creature text such that it is easily parsable
        content_text = format_creature_entry(content_text)
        content_words = content_text.split(' ')
        # update all Creature values
        self._update_abilities(content_words)
        self._update_ac(content_words)
    
    def _update_header_values(self, root):
        '''Updates the values for this Creature that are normally 
        found in the header section of a Monster entry: name, CR, MR
        
        This is done using data in root of HtmlElement tree 
        corresponding to the Creature's page on d20pfsrd.com.
        
        :param root: root element of an HtmlElement tree
        '''
        # get html element with creature's name and CR
        info_element = root.cssselect('td.sites-layout-tile tr')
        # get separate strings for the creature's name and CR
        info_text = info_element[0].text_content()
        info_text = info_text.strip()
        # replace all occurrences of white space with a single ' '
        info_text = re.sub(r"\s+", ' ', info_text)
        # get creature's name and CR
        creature_name = info_text[:info_text.index('CR')-1]
        creature_cr = info_text[info_text.index('CR'):]
        # update creature after formatting
        self.name = format_creature_name(creature_name)
        # update creature CR and MR after extraction from text
        cr_mr_tuple = get_cr_and_mr_from_text(creature_cr)
        self.cr = cr_mr_tuple[0]
        self.mr = cr_mr_tuple[1]
        
    def is_valid(self):
        '''Determines whether or not the Creature object has valid 
        attribute values
        
        :returns True if Creature object is valid, False otherwise
        '''
        # TODO: write this method
        return False

    def update_via_htmlelement(self, root):
        '''Updates the Creature object using data in root element 
        of a Bestiary page from d20pfsrd.com
        
        :param root: root element of an HtmlElement tree created
        '''
        try:
            self._update_header_values(root)
            self._update_entry_values(root)
        except IOError:
            print 'ERROR: failed to update creature data'

    def update_via_list(self, attr_list):
        '''Updates the Creature object using a list of creature 
        attributes taken from a .csv file
        
        :param attr_list: list of attributes (strings) from .csv file
        '''
        self.cr = attr_list[0]
        self.name = attr_list[1]
        self.ability_scores['Str'] = attr_list[2]
        self.ability_scores['Dex'] = attr_list[3]
        self.ability_scores['Con'] = attr_list[4]
        self.ability_scores['Int'] = attr_list[5]
        self.ability_scores['Wis'] = attr_list[6]
        self.ability_scores['Cha'] = attr_list[7]
        self.ac['AC'] = attr_list[8]
        self.ac['touch'] = attr_list[9]
        self.ac['flat-footed'] = attr_list[10]
