'''A module containing a class for building Creature objects from 
root HtmlElement objects related to d20pfsrd.com Bestiary pages'''


import re
import string

from core.creature import Creature


__all__ = ['D20PFSRDCreatureBuilder']


ABILITIES = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
ATTRIBUTES = [
    'DEFENSE', 'hp', 'AC', 'touch', 'flat-footed', 
    'Fort', 'Ref', 'Will', 'Defensive', 'DR', 'Resist', 'Immune', 
    'STATISTICS', 'Base'
]


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
    '''Returns copy of provided Creature entry formatted such that
    it is easily parsable
    
    :param entry: Creature entry scraped from d20pfsrd bestiary page
    :returns: a formatted copy of the Creature entry
    '''
    # handle unicode characters
    _entry = entry.replace(u'\xe2', u'-')
    _entry = _entry.encode('ascii', 'ignore')
    # massage text in some necessary ways
    _entry = _entry.replace('*', '')
    _entry = _entry.replace('flatfooted', 'flat-footed')
    _entry = _entry.replace('Reflex', 'Ref')
    # add spaces where needed
    _entry = _entry.replace(',', ', ')
    _entry = _entry.replace('(', ' (')
    _entry = check_text_for_spaces(_entry, ATTRIBUTES)
    _entry = check_text_for_spaces(_entry, ABILITIES, _entry.find('STATISTICS'))
    # replace all occurrences of white space with a single ' '
    _entry = re.sub(r'\s+', ' ', _entry)
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
    Creature's Challenge Rating (CR) and Mythic Rank (MR)
    
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


class D20PFSRDCreatureBuilder():
    '''Class for building Creature objects from root HtmlElement 
    objects of d20pfsrd.com Bestiary pages'''
    
    def _populate_ability_scores(self, words, creature):
        '''Populates a Creature object's ability score values using 
        the Creature's entry on d20pfsrd.com split into individual 
        words
        
        :param words: text of d20pfsrd bestiary page as list of words
        :param creature: Creature object to be populated
        '''
        for key in creature.ability_scores.keys():
            index = words.index(key, words.index("STATISTICS"))
            parsed_ability = words[index+1]
            parsed_ability = parsed_ability.replace(',', '')
            parsed_ability = parsed_ability.replace(';', '')
            if parsed_ability == '' or '-' in parsed_ability:
                creature.ability_scores[key] = '-1'
            else:
                creature.ability_scores[key] = parsed_ability
    
    def _populate_ac(self, words, creature):
        '''Populates a Creature object's armor class values using the 
        Creature's entry on d20pfsrd.com split into individual words
        
        :param words: text of d20pfsrd bestiary page as list of words
        :param creature: Creature object to be populated
        '''
        for key in creature.ac.keys():
            index = words.index(key, words.index('DEFENSE'))
            parsed_ac = words[index+1]
            parsed_ac = parsed_ac.replace(',', '')
            parsed_ac = parsed_ac.replace(';', '')
            creature.ac[key] = parsed_ac
    
    def _populate_from_header_values(self, root, creature):
        '''Populates a Creature object with values that are normally 
        found in the header section of a d20pfsrd.com Bestiary 
        entry: name, CR, MR
        
        :param root: root element of an HtmlElement tree
        :param creature: Creature object to be populated
        '''
        # get html element with Creature's name and CR
        info_element = root.cssselect('td.sites-layout-tile tr')
        # get separate strings for the Creature's name and CR
        info_text = info_element[0].text_content()
        info_text = info_text.strip()
        # replace all occurrences of white space with a single ' '
        info_text = re.sub(r'\s+', ' ', info_text)
        # get Creature's name and CR
        creature_name = info_text[:info_text.index('CR')-1]
        creature_cr = info_text[info_text.index('CR'):]
        # update Creature after formatting
        creature.name = format_creature_name(creature_name)
        # update Creature CR and MR after extraction from text
        cr_mr_tuple = get_cr_and_mr_from_text(creature_cr)
        creature.cr = cr_mr_tuple[0]
        creature.mr = cr_mr_tuple[1]
    
    def _populate_from_entry_values(self, root, creature):
        '''Populates a Creature object with values that are normally 
        found in the main section of a d20pfsrd.com Bestiary entry
        
        :param root: root element of an HtmlElement tree
        :param creature: Creature object to be populated
        '''
        # get the page's Creature text
        content = root.cssselect('.sites-canvas-main')
        content_element = content[0]
        content_text = content_element.text_content()
        # format Creature text such that it is easily parsable
        content_text = format_creature_entry(content_text)
        content_words = content_text.split(' ')
        # update all Creature values
        self._populate_hp_and_hd(content_words, creature)
        self._populate_ac(content_words, creature)
        self._populate_saves(content_words, creature)
        self._populate_ability_scores(content_words, creature)
    
    def _populate_hp_and_hd(self, words, creature):
        '''Populates a Creature object's hit point and Hit Dice (HD)
        values using the Creature's entry on d20pfsrd.com split into 
        individual words
        
        :param words: text of d20pfsrd bestiary page as list of words
        :param creature: Creature object to be populated
        '''
        # get the Creature's hp value
        index = words.index('hp', words.index('DEFENSE'))
        index = index + 1  # want word after 'hp' in entry
        parsed_hp = words[index]
        parsed_hp = parsed_hp.strip()
        creature.hp = parsed_hp
        # get the Creature's Hit Dice (HD) value
        index = index + 1  # want expression after hp value
        parsed_hd = words[index]
        # handle case where 'each' is after hp value
        if 'each' in parsed_hd:
            index = index + 1
            parsed_hd = words[index]
        parsed_hd = parsed_hd.replace(',', '')
        parsed_hd = parsed_hd.replace(';', '')
        # case 1: hit dice listed in form NdM
        if 'd' in parsed_hd:
            parsed_hd = parsed_hd[1 : parsed_hd.index('d')]
        # case 2: hit diced listed in form N HD
        else:
            parsed_hd = parsed_hd[1:]
        creature.hd = parsed_hd
    
    def _populate_saves(self, words, creature):
        '''Populates a Creature object's saving throw values using the
        Creature's entry on d20pfsrd.coms split into individual
        words
        
        :param words: text of d20pfsrd bestiary page as list of words
        :param creature: Creature object to be populated
        '''
        for key in creature.saves.keys():
            index = words.index(key, words.index('DEFENSE'))
            parsed_save = words[index+1]
            parsed_save = parsed_save.replace(',', '')
            parsed_save = parsed_save.replace(';', '')
            parsed_save = parsed_save.replace('+', '')
            creature.saves[key] = parsed_save
    
    def build(self, root):
        '''Creates a Creature object using data in root HtmlElement 
        of a Bestiary page from d20pfsrd.com
        
        :param root: root HtmlElement of d20pfsrd.com Bestiary page
        :returns: a Creature object
        '''
        creature = Creature()
        # populate Creature object with values
        self._populate_from_header_values(root, creature)
        self._populate_from_entry_values(root, creature)
        return creature
