#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
check if a given page is returning an open directory
'''
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

directory_strings = [
    'Index of'
]

def main(requestobject):
    for item in directory_strings:
        if item in requestobject.text:
            print('potential open directory - {}'.format(requestobject.url))
        else:
            print('{} does not appear to be an open directory'.format(requestobject.url))
