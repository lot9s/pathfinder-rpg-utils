'''A module containing a class for storing Creature objects in a 
SQLite database.'''


import sqlite3


__all__ = ['CreatureDB']


COLUMNS = ("id integer primary key autoincrement", "name varchar(45)", 
           "Str integer", "Dex integer", "Con integer", 
           "Int integer", "Wis integer", "Cha integer", 
           "ac integer", "touch_ac integer", "flatfooted_ac integer")


class CreatureDB(object):
    '''Class for storing Creature objects in a SQLite database.'''
    
    def __init__(self, name='creature.db'):
        self.tables = []
        self.connection = sqlite3.connect(name)
        self.connection.text_factory = str
        
    def add_creature(self, creature):
        '''
        Adds a Creature object as a row in the appropriate table of the SQLite 
        database.
        
        :param creature: a Creature object to be added to the database
        '''
        values = (creature.name,
                  creature.ability_scores['Str'], 
                  creature.ability_scores['Dex'], 
                  creature.ability_scores['Con'], 
                  creature.ability_scores['Int'], 
                  creature.ability_scores['Wis'], 
                  creature.ability_scores['Cha'],
                  creature.ac['AC'], 
                  creature.ac['touch'], 
                  creature.ac['flat-footed'])
        query = '''insert into "%s" 
                   (name,Str,Dex,Con,Int,Wis,Cha,ac,touch_ac,flatfooted_ac) 
                   values (?,?,?,?,?,?,?,?,?,?)''' % creature.cr
        self.connection.execute(query, values)
    
    def commit_and_close(self):
        '''
        Commits any uncommitted changes to the SQLite database and closes the 
        connection
        '''
        self.connection.commit()
        self.connection.close()
        
    def create_table(self, name):
        '''
        Creates a SQLite table with the given name for storing Creature objects 
        if it does not already exist. The table will have columns for names and 
        AC values.
    
        :param name: a string value for the name of the table
        '''
        if name in self.tables:
            return
        # create table
        query_values = (name,) + COLUMNS
        query = '''create table if not exists "%s" 
                   (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''' % query_values
        self.connection.execute(query)
        # add table name to list of tables
        self.tables.append(name)
