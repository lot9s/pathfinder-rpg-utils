'''This module contains a script for generating Pathfinder character
sheets in LaTeX'''


import argparse
import fileinput
import os
import shutil


__all__ = []


def find_and_replace(file_name, find_text, replacement_text):
    '''Finds and replaces text in a file with different text

    :param file_name: the name of the relevant file
    :param find_text: the text that will be found and replaced
    :param replacement_text: the new text to replace the old
    '''
    for line in fileinput.input(file_name, inplace=True):
        print line.replace(find_text, replacement_text).rstrip()


def parse_cmd_args():
    '''Parses command line arguments
    
    :returns map data structure containing each argument and associated value
    '''
    # create parser for command line arguments
    help_desc = 'Generates LaTeX character sheets for the Pathfinder RPG'
    parser = argparse.ArgumentParser(description=help_desc)

    # -argument- name of new character
    parser.add_argument('char-name', help='name of new character')

    # -argument- sets destination directory for output
    parser.add_argument('dest', help='destination directory for output')

    # parse command line arguments
    args = vars(parser.parse_args())
    return args

def set_char_name(char_dir, char_name, prev_value='character'):
    '''Sets a character's name within a character sheet
    
    :param char_dir directory containing the character sheet
    :param char_name desired character name 
    '''
    # replace the current character name with char_name
    find_and_replace(char_dir + '/main.tex', prev_value, char_name)
    find_and_replace(char_dir + '/character.tex', 
                     prev_value.upper(), char_name.upper())
    
    # rename the relevant .tex files to reflect the change in character name
    os.rename('%s/%s.tex' % (char_dir, prev_value),
              '%s/%s.tex' % (dest_dir, char_name))


# --- Script ---
if __name__ == '__main__':
    # parse command line arguments
    args = parse_cmd_args()

    dest_dir = args['dest'] + args['char-name']
    char_name = args['char-name'].lower()

    # create a new character sheet at the desired destination
    shutil.copytree('template/Character Sheet', dest_dir)
    set_char_name(dest_dir, char_name)
    
