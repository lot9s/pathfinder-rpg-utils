'''A module containing a class for representing and manipulating 
creature information from the Pathfinder RPG'''


import re
import string


__all__ = ['Creature']


ABILITIES = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
ATTRIBUTES = [
    'DEFENSE', 'hp', 'AC', 'touch', 'flat-footed', 
    'Fort', 'Ref', 'Will', 'Defensive', 'DR', 'Resist', 'Immune', 
    'STATISTICS', 'Base'
]


class Creature(object):
    '''Class representing a Creature from the Pathfinder RPG'''
    
    def __init__(self):
        self.name = ''
        self.cr = '0'
        self.mr = '0'
        # defenses
        self.hp = '0'
        self.hd = '0'
        self.ac = {'AC': '0', 'touch': '0', 'flat-footed': '0'}
        self.saves = {'Fort': '0', 'Ref': '0', 'Will': '0'}
        # statistics
        self.ability_scores = {
            'Str': '0', 'Dex': '0', 'Con': '0', 
            'Int': '0', 'Wis': '0', 'Cha': '0'
        }
        self.bab = '0'
        self.cmb = '0'
        self.cmd = '0'
        
    def __repr__(self):
        values = [
            self.cr, self.name, '\n',
            self.hp, self.hd, str(self.ac), str(self.saves), '\n',
            str(self.ability_scores), self.bab, self.cmb, self.cmd
        ]
        return ' '.join(values)
    
    def __str__(self):
        values = [
            self.cr, self.name, '\n',
            'hp', self.hp, 
            'HD', self.hd, '\n',
            'AC', self.ac['AC'],
            'touch', self.ac['touch'],
            'flat-footed', self.ac['flat-footed'], '\n',
            'Fort', self.saves['Fort'], 
            'Ref', self.saves['Ref'],
            'Will', self.saves['Will'], '\n',
            'Str', self.ability_scores['Str'],
            'Dex', self.ability_scores['Dex'],
            'Con', self.ability_scores['Con'],
            'Int', self.ability_scores['Int'],
            'Wis', self.ability_scores['Wis'],
            'Cha', self.ability_scores['Cha'], '\n',
            'BAB', self.bab,
            'CMB', self.cmb,
            'CMD', self.cmd, '\n\n'
        ]
        return ' '.join(values)
