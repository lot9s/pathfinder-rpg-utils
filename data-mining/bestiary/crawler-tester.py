'''A module that tests the basic functionality of functions and classes in the crawler module.'''

import crawler
import unittest

class TestPFCreatureInfo(unittest.TestCase):
    '''This class tests the validity of crawler.PFCreatureInfo'''
    def test_update_name_and_cr(self):
        creature = crawler.PFCreatureInfo()
        # Case 1 - Name and CR are in table header
        creature.update('http://www.d20pfsrd.com/bestiary/monster-listings/aberrations/akata')
        self.assertEqual(creature.name, 'Akata')
        self.assertEqual(creature.cr, 'CR 1')

if __name__ == '__main__':
    unittest.main()