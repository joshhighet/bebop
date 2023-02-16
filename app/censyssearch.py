#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
from censys.search import CensysHosts

log = logging.getLogger(__name__)

CENSYS_API_ID = os.getenv('CENSYS_API_ID', None)
CENSYS_API_SECRET = os.getenv('CENSYS_API_SECRET', None)

if CENSYS_API_SECRET and CENSYS_API_ID:
    api = CensysHosts(api_id=CENSYS_API_ID, api_secret=CENSYS_API_SECRET)

def query(search):
    findings = []
    if not (CENSYS_API_ID or CENSYS_API_ID):
        log.error("censys: without an api key queries are skipped")
        return findings
    try:
        log.debug('censys: querying %s', search)
        results = api.search(
            f'services.http.response.html_tags="<title>{search}</title>"'
        )
        records = results.view_all()
        log.info('censys: found %s results for %s', len(records), search)
        if len(records) > 20:
            log.warning('censys: a large number of findings here is abnormal. review results carefully!')
        for result in records:
            findings.append(result)
            log.debug('censys: found %s', result)
    except Exception as sae:
        log.error('censys: api error: %s', sae)
    return findings
