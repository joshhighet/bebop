#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
check if a given page is returning an open directory
'''
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

directory_strings = [
    'Index of'
]

def main(requestobject):
    for item in directory_strings:
        if item in requestobject.text:
            logging.info('potential open directory - {}'.format(requestobject.url))
        else:
            logging.debug('{} does not appear to be an open directory'.format(requestobject.url))
