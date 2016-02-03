'''A module containing functions and classes for representing and manipulating creature information from the Pathfinder RPG'''


import re
import string


class Creature:
    '''Object representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
        self.ac = {'AC': 0, 'touch': 0, 'flat-footed': 0}
    
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
        return formatted_cr
        
    def format_entry(self, entry):
        '''
        Returns copy of creature entry formatted such that it is easily parsable
        
        :param entry: text of creature entry taken from a d20pfsrd bestiary page
        :returns: a formatted copy of the Creature entry
        '''
        new_entry = entry.encode('ascii', 'ignore') # remove unicode characters
        new_entry = new_entry.replace(",", ", ")    # replace all ',' with ', ' for better str.split() behavior
        new_entry = new_entry.replace("flatfooted", "flat-footed")
        new_entry = re.sub(r"\s+", ' ', new_entry)  # replace all occurrences of white space with a single ' '
        for attribute in ['AC', 'touch', 'flat-footed']:
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
        index = words.index(type)
        parsed_ac = words[index+1]
        parsed_ac = parsed_ac.replace(",", "")
        parsed_ac = parsed_ac.replace(";", "")
        self.ac[type] = parsed_ac

    def update(self, root):
        '''
        Updates the Creature object using data in root.
        
        :param root: root element of an HtmlElement tree created from a d20pfsrd bestiary page
        '''
        try:
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(root)
            self.update_ac(root)
            print self.cr, self.name, "\t\t", \
                "AC " + self.ac['AC'], "touch " + self.ac['touch'], "flat-footed " + self.ac['flat-footed']
        except IOError:
            print 'ERROR: problem encountered in Creature.update()'
            
    def update_ac(self, root):
        '''
        Updates the Creature object's AC using data in root.
        
        :param root: root element of an HtmlElement tree created from a d20pfsrd bestiary page
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
        Updates the Creature object's name and CR using data in root.
        
        :param root: root element of an HtmlElement tree created from a d20pfsrd bestiary page
        '''
        # <td> element contains Name and CR
        info_element = root.cssselect('td.sites-layout-tile th')
        # <th> element contains Name and CR
        if not info_element:
            info_element = root.cssselect('td.sites-layout-tile td')
        
        child_l = info_element[0]
        child_r = info_element[1]
        self.name = self.format_name(child_l.text_content().strip())
        self.cr = self.format_cr(child_r.text_content().strip())
