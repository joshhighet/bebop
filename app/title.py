#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(requestobject):
    soup = BeautifulSoup(requestobject.text, 'html.parser')
    for title in soup.find_all('title'):
        logging.info('title: ' + title.get_text())
