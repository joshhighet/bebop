#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shodan
import logging

log = logging.getLogger(__name__)

SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', None)

if SHODAN_API_KEY:
    api = shodan.Shodan(SHODAN_API_KEY)

def query(query):
    findings = []
    if not SHODAN_API_KEY:
        log.error("shodan: without an api key queries are skipped")
        return findings
    try:
        log.debug('shodan: querying %s', query)
        results = api.search(query)
        log.info('shodan: found %s results for %s', results['total'], query)
        if results['total'] > 20:
            log.warning('shodan: a large number of findings here is abnormal. review results carefully!')
        for result in results['matches']:
            findings.append(result)
            log.debug('shodan: found %s', result['ip_str'])
            log.debug('shodan: %s', result['data'])
    except shodan.APIError as sae:
        log.error('shodan: api error: %s', sae)
    return findings
