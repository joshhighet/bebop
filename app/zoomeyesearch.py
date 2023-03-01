#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import logging

log = logging.getLogger(__name__)

ZOOMEYE_API_KEY = os.getenv('ZOOMEYE_API_KEY', None)

def query(squery):
    findings = []
    if not ZOOMEYE_API_KEY:
        log.error("zoomeye: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("zoomeye: no query provided")
        return findings
    log.debug('zoomeye: querying %s', squery)
    results = requests.get('https://api.zoomeye.org/host/search',
                           params={'query': squery},
                           headers={'API-KEY': ZOOMEYE_API_KEY})
    if results.status_code != 200:
        log.error('zoomeye: api error (%s): %s', results.status_code, results.text)
    log.info('zoomeye: found %s results for %s', results.json()['total'], squery)
    if results.json()['total'] > 20:
        log.warning('zoomeye: a large number of findings here is abnormal. review results carefully!')
    for result in results.json()['matches']:
        findings.append(result)
        log.debug('zoomeye: found %s', result['ip'])
        log.debug('zoomeye: %s', result['portinfo']['banner'])
    return findings
