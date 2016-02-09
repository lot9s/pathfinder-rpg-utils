'''A module containing a class for representing and manipulating creature 
information from the Pathfinder RPG'''


import re
import string


__all__ = ['Creature']


class Creature(object):
    '''Class representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
        self.ac = {'AC': 0, 'touch': 0, 'flat-footed': 0}
        
    def __repr__(self):
        return ' '.join([self.cr, self.name, '\t', str(self.ac)])
        
    def format_cr(self, cr):
        '''
        Returns copy of CR argument formatted appropriately
        
        :param cr: a string containing an unformatted Creature CR
        :returns: a formatted Creature CR
        '''
        formatted_cr = cr
        # handle case where space between CR and number has been omitted
        if not formatted_cr[:3] == 'CR ':
            formatted_cr = cr[:2] + ' ' + cr[2:]
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
            formatted_cr = 'CR ' + str(cr + mr / 2)
            if not mr % 2 == 0:
                formatted_cr = formatted_cr + ' 1/2'
        # replace any occurrence of * with ''
        formatted_cr = formatted_cr.replace('*', '')
        return formatted_cr
        
    def format_entry(self, entry):
        '''
        Returns copy of creature entry formatted such that it is easily parsable
        
        :param entry: text of creature entry taken from a d20pfsrd bestiary page
        :returns: a formatted copy of the Creature entry
        '''
        new_entry = entry.encode('ascii', 'ignore') # remove unicode characters
        new_entry = new_entry.replace("*", "")      
        new_entry = new_entry.replace(",", ", ")    
        new_entry = new_entry.replace("flatfooted", "flat-footed")
        new_entry = re.sub(r"\s+", ' ', new_entry)  
        for attribute in ['DEFENSE', 'AC', 'touch', 'flat-footed']:
            index = new_entry.find(attribute)
            if new_entry[index + len(attribute)] != ' ':
                new_entry = new_entry[:index + len(attribute)] + ' ' + new_entry[index + len(attribute):]
        return new_entry
    
    def format_name(self, name):
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
        index = new_name.find('-') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        # capitalize words following a left parenthesis
        index = new_name.find('(') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        return new_name
        
    def parse_ac(self, type, words):
        '''
        Parses one type of AC value from the text of a d20pfsrd bestiary page
        
        :param: type: the type {ac, flat-footed, touch} of AC to be parsed
        :param: words: the text of a d20pfsrd bestiary page as a list of words
        '''
        index = words.index(type, words.index("AC")) # search for AC values after initial occurrence of 'AC'
        parsed_ac = words[index+1]
        parsed_ac = parsed_ac.replace(",", "")
        parsed_ac = parsed_ac.replace(";", "")
        self.ac[type] = parsed_ac
            
    def update_ac(self, root):
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
        content_text = self.format_entry(content_text)
        content_words = content_text.split(' ')
        # get AC values
        self.parse_ac('AC', content_words)
        self.parse_ac('touch', content_words)
        self.parse_ac('flat-footed', content_words)
    
    def update_name_and_cr(self, root):
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
        
        creature_name = info_text[:info_text.index('CR')-1]
        creature_cr = info_text[info_text.index('CR'):]
        
        # update creature name and cr after formatting
        self.name = self.format_name(creature_name)
        self.cr = self.format_cr(creature_cr)

    def update_via_htmlelement(self, root):
        '''
        Updates the Creature object using data in root element of a Bestiary 
        page from d20pfsrd.com
        
        :param root: root element of an HtmlElement tree created
        '''
        try:
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(root)
            self.update_ac(root)
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
        self.ac['AC'] = attr_list[2]
        self.ac['touch'] = attr_list[3]
        self.ac['flat-footed'] = attr_list[4]
