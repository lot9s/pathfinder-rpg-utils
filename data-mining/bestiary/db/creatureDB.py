'''A module containing a class for storing Creature objects in a 
SQLite database.'''


import csv
import sqlite3


__all__ = ['CreatureDB']


class CreatureDB(object):
    '''Class for storing Creature objects in a SQLite database.'''
    
    def __init__(self, name='creature.db', use_nominal_cr=False):
        self.using_nominal_cr = use_nominal_cr
        # initialize database
        self.connection = sqlite3.connect(name)
        self.connection.text_factory = str
        self._create_table()
    
    def _construct_table_columns(self):
        '''Constructs a tuple that defines the columns in 
        the "creatures" table
        
        :returns tuple that defines the columns in "creatures" table
        '''
        columns = ('id integer primary key autoincrement',
                   'name varchar(45)')
        # set type of CR column depending on flag
        if self.using_nominal_cr:
            columns = columns + ('CR varchar(10)',)
        else:
            columns = columns + ('CR real',)
        # add the remaining database fields to column tuple
        main_entry_columns = (
            'hp integer',
            'ac integer', 'touch_ac integer', 'flatfooted_ac integer',
            'Str integer', 'Dex integer', 'Con integer', 
            'Int integer', 'Wis integer', 'Cha integer'
        )
        columns = columns + main_entry_columns
        return columns
    
    def _construct_table_insert_values(self, creature):
        '''Constructs a tuple of Creature values for insertion into
        the "creatures" table
        
        :returns tuple of values for insertion into "creatures" table
        '''
        values = (creature.name,)
        # set value of CR column depending on flag
        if self.using_nominal_cr:
            values = values + ('CR ' + creature.cr,)
        else:
            values = values + (creature.cr,)
        # add the remaining database fields to values tuple
        main_entry_values = (
            creature.hp,
            creature.ac['AC'], 
            creature.ac['touch'], 
            creature.ac['flat-footed'],
            creature.ability_scores['Str'], 
            creature.ability_scores['Dex'], 
            creature.ability_scores['Con'], 
            creature.ability_scores['Int'], 
            creature.ability_scores['Wis'], 
            creature.ability_scores['Cha']
        )
        values = values + main_entry_values
        return values
    
    def _create_table(self):
        '''Creates a SQLite table with the given name for storing 
        Creature objects if it does not already exist
    
        :param name: a string value for the name of the table
        '''
        # create table
        columns = self._construct_table_columns()
        query = '''create table if not exists creatures 
                   (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''' % columns
        self.connection.execute(query)
    
    def add_creature(self, creature):
        '''Adds a Creature object as a row in the appropriate table 
        of the SQLite database
        
        :param creature: a Creature object to be added to the database
        '''
        # ignore duplicate creatures
        if self.is_creature_in_db(creature):
            return
        # insert creature into database
        values = self._construct_table_insert_values(creature)
        query = '''insert into creatures 
                   (
                       name,CR,
                       hp,ac,touch_ac,flatfooted_ac,
                       Str,Dex,Con,Int,Wis,Cha
                   ) 
                   values (?,?,?,?,?,?,?,?,?,?,?,?)'''
        self.connection.execute(query, values)
    
    def commit_and_close(self):
        '''Commits any uncommitted changes to the SQLite database and 
        closes the connection
        '''
        self.connection.commit()
        self.connection.close()
    
    def export_as_csv(self, file_name='creature.csv'):
        '''Exports the data in this object as a .csv file.
        
        :param file_name: the name of the output csv file
        '''
        cursor = self.connection.cursor()
        data = cursor.execute('select * from creatures')
        # write data to output file
        csv_file = open(file_name, 'w')
        writer = csv.writer(csv_file)
        writer.writerow([
            'id', 
            'name', 'CR',
            'hp', 'ac', 'touch_ac', 'flatfooted_ac',
            'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha'
        ])
        writer.writerows(data)
        csv_file.close()
        
    def is_creature_in_db(self, creature):
        ''' Determines whether or not a datbase entry exists for a
        given creature
        
        :returns True if entry exists, False otherwise
        '''
        # set value of CR column depending on flag
        creature_cr = creature.cr
        if self.using_nominal_cr:
            creature_cr = 'CR ' + creature.cr
        # query database for creature
        values = (creature.name, creature_cr)
        query = '''select * from creatures where name=? and cr=?'''
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        
        return cursor.fetchone() != None
