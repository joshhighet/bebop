#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shodan
import logging

log = logging.getLogger(__name__)

SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', None)

if SHODAN_API_KEY:
    api = shodan.Shodan(SHODAN_API_KEY)

def query(squery):
    findings = []
    if not SHODAN_API_KEY:
        log.error("shodan: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("shodan: no query provided")
        return findings
    try:
        log.debug('shodan: querying %s', squery)
        results = api.search(squery)
        log.info('shodan: found %s results for %s', results['total'], squery)
        if results['total'] > 20:
            log.warning('shodan: a large number of findings here is abnormal. review results carefully!')
        for result in results['matches']:
            findings.append(result)
            log.debug('shodan: found %s', result['ip_str'])
            log.debug('shodan: %s', result['data'])
    except shodan.APIError as sae:
        log.error('shodan: api error: %s', sae)
    return findings
