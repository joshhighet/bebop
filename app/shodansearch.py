#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shodan
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', None)

if SHODAN_API_KEY:
    api = shodan.Shodan(SHODAN_API_KEY)

common_hashes = []
with open('common/favicon-hashes.txt', 'r', encoding='utf-8') as common_hashes_file:
    for line in common_hashes_file:
        common_hashes.append(line.strip())
    common_hashes_file.close()

def query(query, is_favicon=False):
    findings = []
    if not SHODAN_API_KEY:
        logging.info('shodan: missing api key to search with!')
        return findings
    if is_favicon and query in common_hashes:
        logging.info('favicon hash found in common hashes list, not searching shodan')
        return findings
    try:
        if is_favicon:
            query = 'http.favicon.hash:{}'.format(query)
        logging.info('shodan: querying "{}"'.format(query))
        results = api.search(query)
        logging.info('shodan: found {} results'.format(results['total']))
        for result in results['matches']:
            findings.append(result)
    except shodan.APIError as sae:
        logging.error('shodan: api error: {}'.format(sae))
    return findings
