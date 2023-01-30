#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

common_headers = []
with open('common/headers.txt', 'r', encoding='utf-8') as common_headers_file:
    for line in common_headers_file:
        common_headers.append(line.strip())
    common_headers_file.close()

def main(siterequest):
    data = {
        'etag': None,
        'server': None,
        'cookies': [],
        'interesting_headers': []
    }
    for hedr in siterequest.headers:
        if hedr.lower() not in common_headers:
            logging.info('header: ' + hedr + ' ' + siterequest.headers[hedr])
            if hedr.lower() == 'set-cookie':
                data['cookies'].append(siterequest.headers[hedr])
                continue
            if hedr.lower() == 'etag' or hedr.lower() == 'e-tag':
                data['etag'] = siterequest.headers[hedr]
                continue
            if hedr.lower() == 'server':
                data['server'] = siterequest.headers[hedr]
                continue
            data['interesting_headers'].append(hedr + ':' + siterequest.headers[hedr])
        else:
            logging.debug('header: ' + hedr + ' ' + siterequest.headers[hedr])
    return data
