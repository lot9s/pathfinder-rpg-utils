'''A module containing a class for representing a Pathfinder RPG character.'''


import json

from pf_class import PFClass
from pf_class_instance import PFClassInstance


__all__ = ['PFCharacter']


CLASS_DIR = "res/json/class/"
JSON_EXTENSION = ".json"


class PFCharacter(object):
    '''Class representing a character from the Pathfinder RPG'''
    
    def __init__(self, file_name):
        '''Constructs PFCharacter objects
        
        :param file_name: path to the JSON file for this character
        '''
        json_dict = json.load(open(file_name, 'r'))
        
        # -populate class members-
        self.name = json_dict['name']
        
        # This dictionary represents a character's investment in each of its
        # classes. Each entry is a PFClassInstance object
        self.classes = {}
        # add all classes associated with this character
        for x in json_dict['classes'].keys():
            file_name = CLASS_DIR + x + JSON_EXTENSION
            class_level = json_dict['classes'][x]
            self.__add_class(file_name, class_level)
    
    def __repr__(self):
        values = [self.name, '\n']
        return ' '.join(values)
    
    def __str__(self):
        values = [self.name, '\n']
        # add class information to string representation
        for x in self.classes.keys():
            item = self.classes[x]
            values.extend( [item[1].name, str(item[0])] )
        return ' '.join(values)
    
    def __add_class(self, file_name, level=1):
        '''Associates this character with a new class
        
        This method will do nothing if the class associated with the provided
        file name has already been added to this character.
        
        :param file_name: path to the json file for the desired class
        :param level: number of levels of this class to associate with character
        '''
        new_class = PFClass(file_name)
        
        # update the self.classes dictionary if character does not have levels 
        # in this class
        if not any(x.name == new_class.name for x in self.classes.itervalues()):
            new_entry = PFClassInstance(new_class, level)
            self.classes[new_class.name] = new_entry
    
    def get_template_values(self):
        '''Retrieves a dictionary of values for use with string.Template
        
        :returns: dictionary of values for use with string.Template
        '''
        template_vals = {'name' : self.name, 'NAME' : self.name.upper()}
        
        # iterate over classes dictionary to populate template_vals dictionary
        display_classes = []
        for i, key in enumerate(self.classes.keys()):
            # store some values for convenience
            idx = str(i+1)
            prefix = 'class' + idx
            instance = self.classes[key]
            
            # -add class-related values-
            template_vals[prefix] = instance.name
            template_vals[prefix + '_level'] = instance.level
            
            # add defense-related values
            template_vals[prefix + '_hit_die'] = instance.hit_die
            template_vals[prefix + '_hit_points'] = instance.hit_points
            template_vals[prefix + '_fort'] = instance.saves['Fort']
            template_vals[prefix + '_ref'] = instance.saves['Ref']
            template_vals[prefix + '_will'] = instance.saves['Will']
            
            # add offense-related values
            template_vals[prefix + '_bab'] = instance.bab
            
            # collect LaTeX display-related values
            display_classes.append(instance.name + ' ' + str(instance.level))
        
        # add LaTeX display-related values to template_vals dictionary
        if len(self.classes.keys()) > 1:
            template_vals['display_classes'] = ", ".join(display_classes)
        else:
            template_vals['display_classes'] = display_classes[0]
        
        return template_vals
