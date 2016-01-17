'''A module that tests the basic functionality of functions and classes in the crawler module.'''

import sys
sys.path.append('..')

from bestiary import crawler
import unittest

class TestPFCreatureInfo(unittest.TestCase):
    '''This class tests the validity of crawler.PFCreatureInfo'''
    def test_update_name_and_cr(self):
        creature = crawler.PFCreatureInfo()
        # Case 1 - Name and CR are in table header
        creature.update('http://www.d20pfsrd.com/bestiary/monster-listings/aberrations/akata')
        self.assertEqual(creature.name, 'Akata')
        self.assertEqual(creature.cr, 'CR 1')
        # Case 2 - Name and CR are in table element
        creature.update('http://www.d20pfsrd.com/bestiary/monster-listings/oozes/amoeba-giant')
        self.assertEqual(creature.name, 'Giant Amoeba')
        self.assertEqual(creature.cr, 'CR 1')
        # Case 3 - Name and CR are in table element and surrounded by <b> tag
        creature.update('http://www.d20pfsrd.com/bestiary/monster-listings/vermin/ant/ant-giant-worker')
        self.assertEqual(creature.name, 'Giant Ant Worker')
        self.assertEqual(creature.cr, 'CR 1')
        # Case 3 - Name and CR are in table element and surrounded by <font> tag
        creature.update('http://www.d20pfsrd.com/bestiary/monster-listings/outsiders/elemental/elemental-ice/small-ice-elemental')
        self.assertEqual(creature.name, 'Small Ice Elemental')
        self.assertEqual(creature.cr, 'CR 1')

if __name__ == '__main__':
    unittest.main()