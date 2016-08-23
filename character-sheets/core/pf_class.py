'''A module containing a class for representing a Pathfinder RPG class.'''


import json


class PFClass(object):
    '''Class representing a character class from the Pathfinder RPG'''
    
    def __init__(self, file_name):
        '''Constructs PFClass objects
        
        :param file_name: path to the JSON file for this class
        '''
        json_dict = json.load(open(file_name, 'r'))
        # -populate class members-
        self.name = json_dict['name']
        self.restrictions = json_dict['restrictions']
        self.hit_die = json_dict['hit-die']
        self.base_attack = json_dict['base-attack']
        self.saves = json_dict['saves']
        self.skills = json_dict['skills']
        self.skills_per_level = json_dict['skills-per-level']
        self.starting_wealth = json_dict['starting-wealth'];
        self.advancement = json_dict['advancement']
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
