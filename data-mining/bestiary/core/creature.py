'''A module containing a class for representing and manipulating creature 
information from the Pathfinder RPG'''


import re
import string


__all__ = ['Creature']


# --- Constants ---
ABILITIES = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
ATTRIBUTES = ['DEFENSE', 'AC', 'touch', 'flat-footed', 'STATISTICS', 'Base']


# --- Functions ---
def check_text_for_spaces(text, keywords, start=0):
    '''
    Checks text for spaces before and after certain keywords. If a space is not 
    present, it gets inserted into the text in the appropriate place.
    
    :param text: the text to be checked
    :param keywords: the keywords that require spaces after them in the text
    :param start: starting index in text to begin checking at
    :returns a new version of the given text with spaces where they should be
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
    
def format_creature_cr(cr):
    '''
    Returns copy of CR argument formatted appropriately
    
    :param cr: a string containing an unformatted Creature CR
    :returns: a formatted Creature CR
    '''
    formatted_cr = cr
    # handle case where space between CR and number has been omitted
    if not formatted_cr[:3] == 'CR ':
        formatted_cr = insert_text(cr, 2, ' ')   
    # handle case where creature has a mythic rank
    if 'MR' in cr:
        ranks = formatted_cr.split('/M')
        # get challenge rating
        cr_words = ranks[0].split(' ')
        cr = int(cr_words[1])
        # get mythic rank
        mr_words = ranks[1].split(' ')
        mr = int(mr_words[1])
        # calculate new CR
        formatted_cr = str(cr + mr / 2)
        if not mr % 2 == 0:
            formatted_cr = formatted_cr + '.5'
    # handle standard case
    else:
        cr_words = formatted_cr.split(' ')
        formatted_cr = cr_words[1]
        if '/' in formatted_cr:
            formatted_cr = str(float(formatted_cr[0]) / float(formatted_cr[2]))
            if len(formatted_cr) > 4:
                formatted_cr = formatted_cr[:4]
    # replace any occurrence of * with ''
    formatted_cr = formatted_cr.replace('*', '')
    return formatted_cr
    
def format_creature_entry(entry):
    '''
    Returns copy of creature entry formatted such that it is easily parsable
    
    :param entry: text of creature entry taken from a d20pfsrd bestiary page
    :returns: a formatted copy of the Creature entry
    '''
    _entry = entry.encode('ascii', 'ignore') # remove unicode characters
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
    new_name = name.encode('ascii', 'ignore')   # remove unicode characters
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
    
def insert_text(orig_text, index, insert_text):
    '''
    Inserts a string into another string at a given index and returns it
    
    :param orig_text: the original string
    :param index: index of original string to insert text into
    :param insert_text: the string that will be inserted into the original
    :returns the new string after the insertion
    '''
    return "%s%s%s" % (orig_text[:index], insert_text, orig_text[index:])


# --- Classes ---
class Creature(object):
    '''Class representing a creature from the Pathfinder RPG'''
    
    def __init__(self):
        self.name = ""
        self.cr = 0
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
        '''
        Updates the Creature's ability score values using the Creature's entry
        on d20pfsrd.com split into individual words
        
        :param words: the text of a d20pfsrd bestiary page as a list of words
        '''
        for key in self.ability_scores.keys():
            index = words.index(key, words.index("STATISTICS"))
            parsed_ability = words[index+1]
            parsed_ability = parsed_ability.replace(",", "")
            parsed_ability = parsed_ability.replace(";", "")
            self.ability_scores[key] = parsed_ability
        
    def _update_ac(self, words):
        '''
        Updates the Creature's armor class values using the Creature's entry
        on d20pfsrd.com split into individual words
        
        :param words: the text of a d20pfsrd bestiary page as a list of words
        '''
        for key in self.ac.keys():
            index = words.index(key, words.index("AC"))
            parsed_ac = words[index+1]
            parsed_ac = parsed_ac.replace(",", "")
            parsed_ac = parsed_ac.replace(";", "")
            self.ac[key] = parsed_ac
        
    def _update_values(self, root):
        '''
        Updates the Creature object's AC using data in root of HtmlElement tree
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
    
    def _update_name_and_cr(self, root):
        '''
        Updates the Creature object's name and CR using data in root of 
        HtmlElement tree corresponding to the Creature's page on d20pfsrd.com
        
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
        # update creature name and cr after formatting
        self.name = format_creature_name(creature_name)
        self.cr = format_creature_cr(creature_cr)
        
    def is_valid(self):
        '''
        Determines whether or not the Creature object has valid attribute values
        
        :returns True if Creature object is valid, False otherwise
        '''
        # TODO: write this method
        return False

    def update_via_htmlelement(self, root):
        '''
        Updates the Creature object using data in root element of a Bestiary 
        page from d20pfsrd.com
        
        :param root: root element of an HtmlElement tree created
        '''
        try:
            self._update_name_and_cr(root)
            self._update_values(root)
        except IOError:
            print 'ERROR: failed to update creature data'

    def update_via_list(self, attr_list):
        '''
        Updates the Creature object using a list of creature attributes taken 
        from a .csv file
        
        :param attr_list: list of attributes (strings) from a .csv file
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
