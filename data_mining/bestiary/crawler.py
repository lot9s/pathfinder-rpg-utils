#!/usr/bin/python
#
#   The purpose of this script is to construct a database of Pathfinder RPG creatures by crawling
#   the d20pfsrd.
#

from lxml.html import parse

def get_creature_info(page):
    '''Obtains information about the creature denoted by the given page.'''
    try:
        parsed_html = parse(page)
        doc = parsed_html.getroot()
    
        name = get_creature_name(doc)

    except IOError:
        return None

def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the given page'''
    parsed_html = parse(page)
    doc = parsed_html.getroot()
    elements = doc.cssselect('div a')
    
    links = []
    for element in elements:
        link = element.get('href')
        if (link != None and 
            "monster-listings/" in link and
            not "-TOHC" in link and
            not "-tohc" in link):           
            links.append(link)
    return links
    
def get_creature_name(doc):
    ''''Obtains creature name from the given document tree.'''
    title = doc.cssselect('title')
    if len(title) > 0:
        name = title[0].text
        if "3pp" in name or "3PP" in name:
            return None
        else:
            name = name.split(' - ')
            return name[0]
    else:
        return None

def get_html_indeces():
    '''Obtains the list of links to pages of creatures clustered by Challenge Rating.'''
    file = open('indeces.txt', 'r')
    indeces = file.readlines()
    for i in range(len(indeces)):
        indeces[i] = indeces[i].rstrip()
    return indeces

# script 
if __name__ == '__main__':
    indeces = get_html_indeces()
    
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        get_creature_info(link)