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

def favicon(mmh3hash):
    findings = []
    if not SHODAN_API_KEY:
        logging.info('no shodan api key to search with!')
        return findings
    if mmh3hash in common_hashes:
        logging.info('favicon hash found in common hashes list, not searching shodan')
        return findings
    try:
        results = api.search('http.favicon.hash:' + str(mmh3hash))
        logging.info('found {} results querying shodan'.format(results['total']))
        for result in results['matches']:
            findings.append(result)
    except shodan.APIError as sae:
        print('shodan api error: {}'.format(sae))
    return findings

def general(query):
    findings = []
    if not SHODAN_API_KEY:
        logging.info('no shodan api key to search with!')
        return findings
    try:
        results = api.search(query)
        logging.info('found {} results querying shodan'.format(results['total']))
        for result in results['matches']:
            findings.append(result)
    except shodan.APIError as sae:
        print('shodan api error: {}'.format(sae))
    return findings
