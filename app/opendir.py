#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
check if a given page is returning an open directory
'''
import logging
log = logging.getLogger(__name__)

directory_strings = [
    'Index of'
]

def main(requestobject):
    for item in directory_strings:
        if item in requestobject.text:
            log.info('potential open directory - %s', requestobject.url)
        else:
            log.debug('%s does not appear to be an open directory', requestobject.url)
