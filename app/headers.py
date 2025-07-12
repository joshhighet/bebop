#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import app.subprocessors as subprocessors

log = logging.getLogger(__name__)

common_headers = []
with open('common/headers.txt', 'r', encoding='utf-8') as common_headers_file:
    for line in common_headers_file:
        common_headers.append(line.strip())
    common_headers_file.close()

def main(siterequest, doshodan=True, docensys=True, dozoome=True, dofofa=True):
    data = {
        'etag': None,
        'server': None,
        'cookies': [],
        'interesting_headers': []
    }
    for hedr in siterequest.headers:
        if hedr.lower() not in common_headers:
            log.info('interesting header: "' + hedr + ': ' + siterequest.headers[hedr] + '"')
            if hedr.lower() == 'set-cookie':
                data['cookies'].append(siterequest.headers[hedr])
                continue
            if hedr.lower() == 'etag' or hedr.lower() == 'e-tag':
                if siterequest.headers[hedr].startswith('W/'):
                    log.warning('the etag found is tagged as a weak validator')
                    data['etag'] = siterequest.headers[hedr].replace('W/', '').strip('"')
                else:
                    data['etag'] = siterequest.headers[hedr].strip('"')
                continue
            if hedr.lower() == 'server':
                data['server'] = siterequest.headers[hedr]
                continue
            data['interesting_headers'].append(hedr + ':' + siterequest.headers[hedr])
        else:
            log.debug('header: ' + hedr + ' ' + siterequest.headers[hedr])
    if 'cf-mitigated' in data['interesting_headers'] and 'cloudflare' in data['server'].lower():
        log.warning('requests are likely getting challenged by cloudflare!')
    if data['etag'] is not None:
        if doshodan:
            subprocessors.query_shodan(data['etag'])
        if docensys:
            subprocessors.query_censys(data['etag'])
        if dozoome:
            subprocessors.query_zoomeye(data['etag'])
        if dofofa:
            subprocessors.query_fofa('header=' + str(data['etag']))
    return data
