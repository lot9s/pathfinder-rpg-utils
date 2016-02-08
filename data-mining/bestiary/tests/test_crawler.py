'''A module that tests the basic functionality of functions and classes in the crawler module.'''


import sys
sys.path.append('..')

import unittest
from lxml.html import parse
from bestiary.core.creature import Creature


class TestCreature(unittest.TestCase):
    '''This class tests the validity of crawler.PFCreatureInfo'''
    LINK_PREFIX = 'http://www.d20pfsrd.com/bestiary/monster-listings/'
    
    def _test_update_name_and_cr(self, link, expected_name, expected_cr):
        '''Executes a single, specific sanity check for Creature.update_name_and_cr(...)'''
        # get root node of an HtmlElement tree representing the provided link
        parsed_html = parse(link)
        root = parsed_html.getroot()
        # create a Crature object populated by information from the provided link
        creature = Creature()
        creature.update(root)
        # check to see if the Creature object's attributes match expectations
        self.assertEqual(creature.name, expected_name)
        self.assertEqual(creature.cr, expected_cr)
        
    def test_update_name_and_cr(self):
        '''Executes a small number of sanity checks for Creature.update_name_and_cr(...)'''
        # standard creature entry
        self._test_update_name_and_cr(self.LINK_PREFIX + 'aberrations/akata', 'Akata', 'CR 1')
        # creature entry uses a non-standard mix of html elements for displaying name and CR
        self._test_update_name_and_cr(self.LINK_PREFIX + 'outsiders/demodand/demodand-tarry', \
                                        'Tarry Demodand', 'CR 13')
    

if __name__ == '__main__':
    unittest.main()
