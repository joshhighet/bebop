#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(requestobject):
    soup = BeautifulSoup(requestobject.text, 'html.parser')
    title = soup.find('title')
    if title is not None:
        logging.info('title: %s', title.text)
        return title.text
    logging.error('no title found on page')
    return None
