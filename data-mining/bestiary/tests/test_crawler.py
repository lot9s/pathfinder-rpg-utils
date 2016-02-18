'''A module that tests the basic functionality of functions and classes 
in the crawler module.'''


import sys
sys.path.append('..')

import unittest
from lxml.html import parse
from bestiary.core.creature import Creature


class TestCreature(unittest.TestCase):
    '''This class tests the validity of crawler.PFCreatureInfo'''
    
    LINK_PREFIX = 'http://www.d20pfsrd.com/bestiary/monster-listings/'
    
    def _test_update_abilities(self, link, expected_abilities):
        '''Executes a single, specific sanity check for 
        Creature.update_name_and_cr(...)
        
        :param link: string containing link to non-3rd party creature
        :param expected_abilities: dictionary of expected ability scores
        '''
        # get root of an HtmlElement tree representing provided link
        parsed_html = parse(link)
        root = parsed_html.getroot()
        # create Creature from root
        creature = Creature()
        creature.update_via_htmlelement(root)
        print creature
        # check if the Creature's attributes match expectations
        for key in creature.ability_scores.keys():
            self.assertEqual(creature.ability_scores[key],
                             expected_abilities[key])
    
    def _test_update_header_values(self, link, expected_name, expected_cr):
        '''Executes a single, specific sanity check for 
        Creature.update_header_values(...)
        
        :param link: string containing link to non-3rd party creature
        :param expected_name: the name of the creature we expect to see
        :param expected_cr: the cr of the creature we expect to see
        '''
        # get root of an HtmlElement tree representing provided link
        parsed_html = parse(link)
        root = parsed_html.getroot()
        # create Creature from root
        creature = Creature()
        creature.update_via_htmlelement(root)
        # check if the Creature's attributes match expectations
        self.assertEqual(creature.name, expected_name)
        self.assertEqual(creature.cr, expected_cr)    
    
    def test_update_abilities(self):
        '''Executes a small number of sanity checks for 
        Creature._update_values(...)
        '''
        # problem - does not get value for CHA
        self._test_update_abilities(
            self.LINK_PREFIX + 'animals/herd-animals/camel',
            {'Str': '18', 'Dex': '16', 'Con': '14', 
             'Int': '2', 'Wis': '11', 'Cha': '4'})
        self._test_update_abilities(
            self.LINK_PREFIX + 'oozes/amoeba-giant',
            {'Str': '12', 'Dex': '1', 'Con': '16', 
             'Int': '-1', 'Wis': '1', 'Cha': '1'})
        
    def test_update_header_values(self):
        '''Executes a small number of sanity checks for 
        Creature._update_name_and_cr(...)
        '''
        # problem - standard creature entry
        self._test_update_header_values(
            self.LINK_PREFIX + 'aberrations/akata', 'Akata', '1')
        # problem - creature entry uses non-standard mix of 
        #               html elements for displaying name and CR
        self._test_update_header_values(
            self.LINK_PREFIX + 'outsiders/demodand/demodand-tarry',
            'Tarry Demodand', '13')
    

if __name__ == '__main__':
    unittest.main()
