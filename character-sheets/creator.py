'''This module contains a script for generating Pathfinder character
sheets in LaTeX'''


import argparse
import fileinput
import os
import shutil

from string import Template

from core.pf_character import PFCharacter


__all__ = []


# --- Constants ---
TEMPLATE_FILES = [
    '/main.tex', 
    '/character.tex',
    '/res/latex/class/class1.tex',
    '/res/latex/stats/defense.tex',
    '/res/latex/stats/offense.tex',
]


def generate_character(dest_path, char_path="default.json"):
    '''Generates a LaTeX project for a Pathfinder character sheet
    
    :param dest_path: destination directory for character sheet
    :param char_path: path to JSON file with Pathfinder character data
    '''
    character = PFCharacter(char_path)
    
    # update the destination path string to reflect imported character vals
    dest_path = "%s/%s" % (dest_path, character.name)
    
    shutil.copytree('template/Character Sheet', dest_path)
    set_char_vals(dest_path, character.get_template_values())


def parse_cmd_args():
    '''Parses command line arguments
    
    :returns map data structure containing each argument and associated value
    '''
    # create parser for command line arguments
    help_desc = 'Generates LaTeX character sheets for the Pathfinder RPG'
    parser = argparse.ArgumentParser(description=help_desc)

    # -argument- sets destination directory for output
    parser.add_argument('dest', help='destination directory for output')

    # -argument [optional]- import character from a JSON file
    parser.add_argument('--import', metavar='PATH',
                        help='imports character data from JSON file')

    # parse command line arguments
    args = vars(parser.parse_args())
    
    return args


def set_char_vals(char_path, char_vals):
    '''Replaces placeholder values in character sheet template with those that
    describe a particular character
    
    :param char_path directory containing the character sheet
    :param char_vals dictionary structured according to string.Template 
    '''
    # replace placeholder values in character sheet template
    for x in TEMPLATE_FILES:
        # read file data
        template_file = open(char_path + x, 'r')
        template_data = template_file.read()
        template_file.close()
        # apply values to template
        replace_text = Template(template_data).substitute(char_vals)
        # write data to file
        template_file = open(char_path + x, 'w')
        template_file.write(replace_text)
        template_file.close()
    
    # rename the character.tex to reflect the change in character name
    os.rename('%s/character.tex' % char_path,
              '%s/%s.tex' % (char_path, char_vals['name']))
    # rename the class1.tex to reflect the change in character name
    new_path_tuple = (char_path, char_vals['class1'])
    os.rename('%s/res/latex/class/class1.tex' % char_path,
              '%s/res/latex/class/%s.tex' % new_path_tuple)
    os.rename('%s/res/latex/class-features/display/class1.tex' % char_path,
              '%s/res/latex/class-features/display/%s.tex' % new_path_tuple)


# --- Script ---
if __name__ == '__main__':
    # parse command line arguments
    args = parse_cmd_args()
    
    # generate character
    if args['import'] is not None:
        generate_character(args['dest'], args['import'])
    else:
        generate_character(args['dest'])
