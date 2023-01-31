#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpage
import logging
log = logging.getLogger(__name__)

import title

interesting_paths = [
    {'uri': '/server-status', 'code': 200, 'text': 'Apache'},
    {'uri': '/server-info', 'code': 200, 'text': 'Apache'},
    {'uri': '/robots.txt', 'code': 200, 'text': None},
    {'uri': '/sitemap.xml', 'code': 200, 'text': None},
]

def main(location):
    if location.endswith('/'):
        location = location[:-1]
    for path in interesting_paths:
        page = getpage.main(location + path['uri'])
        if page is None:
            log.error('no response from {}'.format(location + path['uri']))
            continue
        if page.status_code == path['code']:
            title.main(page)
            if path['text'] is None:
                log.info('found {} at {}'.format(path['code'], location + path['uri']))
            else:
                if path['text'] in page.text:
                    log.info('found {} at {}'.format(path['code'], location + path['uri']))
                else:
                    log.debug('found {} at {} but no match for {}'.format(path['code'], location + path['uri'], path['text']))
        else:
            log.debug('found {} at {}'.format(page.status_code, location + path['uri']))
