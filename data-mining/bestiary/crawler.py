'''A module containing functions and classes that allow one to scrape specific information from the Bestiary pages of d20pfsrd.com'''

from lxml.html import parse


def get_creature_links(page):
    '''Obtains the list of links to all non-3rd party creatures on the given page'''
    parsed_html = parse(page)
    doc = parsed_html.getroot()
    elements = doc.cssselect('div a')
    
    links = []
    for element in elements:
        link = element.get('href')
        if link != None and "monster-listings/" in link and \
           not ('TOC-' in link or 'corgi-dire' in link or \
                link[-5:] == "-TOHC" or link[-5:] == "-tohc" or \
                link[-4:] == '-3PP' or link[-3:] == '-kp' or link[-3:] == '-ff'):           
            links.append(link)
    return links
    
def get_html_indeces():
    '''Obtains the list of links to pages of creatures clustered by Challenge Rating.'''
    file = open('indeces.txt', 'r')
    indeces = file.readlines()
    for i in range(len(indeces)):
        indeces[i] = indeces[i].rstrip()
    return indeces
    
class PFCreatureInfo:
    '''Data structure representing a creature from the Pathfinder RPG'''
    def __init__(self):
        self.name = ""
        self.cr = 0
    
    def find_name_or_cr_text(self, element):
        if len(element) > 0:
            nested_tag = element[0].tag
            print 'tag-single', nested_tag
            # nested element is of type <b>
            if nested_tag == 'b':
                return element[0]
            # nested element is of type <br>
            if nested_tag == 'br':
                return element
            # nested element is of type <font>
            if nested_tag == 'font':
                # doubly-nested element
                if len(element[0]) > 0:
                    nested_element = element[0]
                    nested_tag = nested_element[0].tag
                    print 'tag-double', nested_tag
                    # doubly-nested element is of type <b>
                    if nested_tag == 'b':
                        return nested_element[0]
                    # doubly-nested element is of type <br>
                    if nested_tag == 'br':
                        return element[0]
                else:
                    return element[0]
        else:
            return element
    
    def update_name_and_cr(self, doc):
        '''
        Updates the name and CR of creature from provided DOM object.
        '''
        # <th> element containing Name and CR
        info_element = doc.cssselect('td.sites-layout-tile th')
        
        # <td> element containing Name and CR
        if not info_element:
            info_element = doc.cssselect('td.sites-layout-tile td')
            child_l = info_element[0]
            child_r = info_element[1]
            info_element[0] = self.find_name_or_cr_text(child_l)
            info_element[1] = self.find_name_or_cr_text(child_r)
        
        self.name = info_element[0].text
        self.cr = info_element[1].text
        
    def update(self, page):
        '''Update data structure with data found on the provided page.'''
        try:
            parsed_html = parse(page)
            doc = parsed_html.getroot()
    
            # update the creature's name and Challenge Rating
            self.update_name_and_cr(doc)
            
            print self.cr, self.name
            print ''

        except IOError:
            return None


# script 
if __name__ == '__main__':
    indeces = get_html_indeces()
    
    index = indeces[0]
    links = get_creature_links(index)
    for link in links:
        print link
        PFCreatureInfo().update(link)