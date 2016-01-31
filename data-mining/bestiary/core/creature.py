'''A module containing functions and classes for representing and manipulating creature information from the Pathfinder RPG'''


import string


class Creature:
    '''Object representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
    
    def format_cr(self, cr):
        '''Returns copy or string argument formatted as a proper CR'''
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
    
    def format_name(self, name):
        '''Returns copy of string argument formatted as a proper name'''
        new_name = name.lower()
        # capitalize space-separated words
        new_name = string.capwords(new_name, ' ')
        # capitalize words following a hyphen
        index = new_name.find('-') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        # capitalize words following a left parenthesis
        index = new_name.find('(') + 1
        new_name = new_name[:index] +  new_name[index].upper() + new_name[index+1:]
        return new_name

    def update(self, root):
        '''
        Updates the PFCreatureInfo object using ifnormation gleaned from the
        root of the provided HtmlElement tree.
        '''
        try:
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(root)
            print self.cr, self.name
            print ''
        except IOError:
            return None
    
    def update_name_and_cr(self, root):
        '''
        Updates the name and CR of creature using information gleaned from the
        root of the provided HtmlElement tree.
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