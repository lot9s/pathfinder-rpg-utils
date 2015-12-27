#!/usr/bin/python

from lxml.html import parse
from urllib2 import urlopen
from pandas.io.parsers import TextParser

CREATURE_BY_CR_URL = "http://www.d20pfsrd.com/bestiary/-bestiary-by-challenge-rating"

url_text = []

if __name__ == '__main__':
    parsed_html = parse(CREATURE_BY_CR_URL)