#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import logging

log = logging.getLogger(__name__)

BINARYEDGE_API_KEY = os.getenv('BINARYEDGE_API_KEY', None)

def query(squery):
    findings = []
    if not BINARYEDGE_API_KEY:
        log.error("binaryedge: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("binaryedge: no query provided")
        return findings
    log.debug('binaryedge: querying %s', squery)
    results = requests.get('https://api.binaryedge.io/v2/query/search', params={'query': squery}, headers={'X-Key': BINARYEDGE_API_KEY})
    if results.status_code != 200:
        log.error('binaryedge: api error (%s): %s', results.status_code, results.text)
    log.info('binaryedge: found %s results for %s', results.json()['total'], squery)
    if results.json()['total'] > 20:
        log.warning('binaryedge: a large number of findings here is abnormal. review results carefully!')
    for result in results.json()['events']:
        findings.append(result)
        log.debug('binaryedge: found %s', result['target']['ip'])
        log.debug('binaryedge: %s', result['result']['data']['response']['body']['content'])
    return findings
