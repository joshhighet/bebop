#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import warnings
from bs4 import BeautifulSoup

import shodansearch

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

common_titles = []
with open('common/http-titles.txt', 'r', encoding='utf-8') as common_titles_file:
    for line in common_titles_file:
        common_titles.append(line.strip())
    common_titles_file.close()

def main(requestobject, doshodan=True):
    if len(requestobject.text.splitlines()) == 1:
        logging.error('single line response, not parsing')
        return None
    soup = BeautifulSoup(requestobject.text, 'html.parser')
    title = soup.find('title')
    if title is not None:
        logging.info('title: %s', title.text)
        if doshodan and title.text not in common_titles:
            shodansearch.query('http.title:"' + title.text + '"')
        return title.text
    logging.error('no title found on page')
    logging.debug('page source: %s', requestobject.text)
    return None
