'''A module containing a class for representing a Pathfinder RPG 
character\'s investment in a particular character class'''


from pf_class import PFClass


__all__ = ['PFClassInstance']


class PFClassInstance(object):
    '''Class representing a Pathfinder RPG character\'s investment in a 
    particular character class'''
    
    def __init__(self, _class, _level=1):
        '''Constructs PFClassInstance objects
        
        :param _class: a PFClass object
        :param _level: number of levels invested in class, defaults to 1
        '''
        self.__class = _class
        self.name = _class.name
        
        self.level = _level
        
        # calculate hit points
        self.hit_points = 0
        self.hit_die = _class.hit_die
        self.__calculate_hit_points()
        
        # calculate base attack bonus
        self.bab = _class.base_attack * self.level
        
        # calculate saving throws
        self.saves = {}
        self.__calculate_saving_throws()
    
    def __calculate_bad_saving_throw(self):
        return self.level / 3
    
    def __calculate_good_saving_throw(self):
        return 2 + (self.level / 2)
    
    def __calculate_hit_points(self):
        if self.level == 1:
            self.hit_points = self.hit_die
        else:
            hp_per_level = (self.hit_die / 2) + 1
            self.hit_points = self.hit_die + (hp_per_level * (self.level - 1))
    
    def __calculate_saving_throws(self):
        for key in self.__class.saves.keys():
            if self.__class.saves[key] == 1:
                self.saves[key] = self.__calculate_good_saving_throw()
            else:
                self.saves[key] = self.__calculate_bad_saving_throw()

