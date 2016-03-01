'''A module containing a function for building Creature objects from a 
dictionary of features'''


from core.creature import Creature


__all__ = ['build']


def build(dict_):
    '''Creates a Creature object from the given a dictionary of 
    features
    
    :param dict_: dictionary of featurees
    :returns: a Creature object
    '''
    creature = Creature()
    # populate Creature object with values
    creature.cr = dict_['CR']
    creature.name = dict_['name']
    creature.hp = dict_['hp']
    creature.hd = dict_['HD']
    for key in creature.ac.keys():
        creature.ac[key] = dict_[key]
    for key in creature.saves.keys():
        creature.saves[key] = dict_[key]
    for key in creature.ability_scores.keys():
        creature.ability_scores[key] = dict_[key]
    creature.bab = dict_['BAB']
    return creature
