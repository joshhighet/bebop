#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpage
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

interesting_paths = [
    {'uri': '/server-status', 'code': 200, 'text': 'Apache'},
    {'uri': '/server-info', 'code': 200, 'text': 'Apache'},
    {'uri': '/robots.txt', 'code': 200, 'text': None},
    {'uri': '/sitemap.xml', 'code': 200, 'text': None},
]

def main(location):
    for path in interesting_paths:
        page = getpage.main(location + path['uri'])
        if page.status_code == path['code']:
            # if we have text to match, check it
            if path['text'] is None:
                print('found {} at {}'.format(path['code'], location + path['uri']))
            else:
                if path['text'] in page.text:
                    print('found {} at {}'.format(path['code'], location + path['uri']))
                else:
                    print('found {} at {} but no match for {}'.format(path['code'], location + path['uri'], path['text']))
        else:
            print('found {} at {}'.format(page.status_code, location + path['uri']))
