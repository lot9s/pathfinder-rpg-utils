'''A module containing a class for building Creature objects from a 
list of attributes'''


from core.creature import Creature


class ListCreatureBuilder:
    '''Class for building Creature objects from a list of 
    attributes'''
    
    def build(self, list_):
        '''Creates a Creature object from the given list of 
        attributes
        
        :param list_: list of attributes
        :returns: a Creature object
        '''
        creature = Creature()
        creature.cr = list_[0]
        creature.name = list_[1]
        creature.hp = list_[2]
        creature.hd = list_[3]
        creature.ac['AC'] = list_[4]
        creature.ac['touch'] = list_[5]
        creature.ac['flat-footed'] = list_[6]
        creature.saves['Fort'] = list_[7]
        creature.saves['Ref'] = list_[8]
        creature.saves['Will'] = list_[9]
        creature.ability_scores['Str'] = list_[10]
        creature.ability_scores['Dex'] = list_[11]
        creature.ability_scores['Con'] = list_[12]
        creature.ability_scores['Int'] = list_[13]
        creature.ability_scores['Wis'] = list_[14]
        creature.ability_scores['Cha'] = list_[15]
        return creature
