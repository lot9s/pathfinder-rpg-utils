#!/usr/bin/python

import HTMLParser
import urllib

CREATURE_BY_CR_URL = "http://www.d20pfsrd.com/bestiary/-bestiary-by-challenge-rating"

url_text = []

class MyHTMLParser(HTMLParser.HTMLParser):
    def handle_data(self, data):
        if data != '\n':
            url_text.append(data)

if __name__ == '__main__':
    page_ref = urllib.urlopen(CREATURE_BY_CR_URL)
    page_html = page_ref.read()

    parser = MyHTMLParser()
    parser.feed(page_html)
    parser.close()

    for element in url_text:
        print element