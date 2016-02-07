'''A module containing a class for storing Creature objects in a SQLite database.'''


import sqlite3


class CreatureDB(object):
    '''Class for storing Creature objects in a SQLite database.'''
    def __init__(self, name='creature.db'):
        self.tables = []
        self.connection = sqlite3.connect(name)
        self.connection.text_factory = str
        
    def add_creature(self, creature):
        '''
        Adds a Creature object as a row in the appropriate table of the SQLite database.
        
        :param creature: a Creature object to be added to the database
        '''
        values = (creature.name, creature.ac['AC'], creature.ac['touch'], creature.ac['flat-footed'])
        query = 'insert into "'+ creature.cr +'" (name, ac, touch_ac, flatfooted_ac) values (?,?,?,?)'
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
        if it does not already exist. The table will have columns for names and AC values.
    
        :param name: a string value for the name of the table
        '''
        if name in self.tables:
            return
        # create table
        query = 'create table if not exists "' + name + '" ('
        query = query + 'id integer primary key autoincrement, name varchar(35), '
        query = query + 'ac integer, touch_ac integer, flatfooted_ac integer)'
        self.connection.execute(query)
        # add table name to list of tables
        self.tables.append(name)
