#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import base64
import logging
import requests
from censys.search import CensysHosts
from censys.common.exceptions import CensysException
import shodan

log = logging.getLogger(__name__)
ZOOMEYE_API_KEY = os.getenv('ZOOMEYE_API_KEY', None)
BINARYEDGE_API_KEY = os.getenv('BINARYEDGE_API_KEY', None)
CENSYS_API_ID = os.getenv('CENSYS_API_ID', None)
CENSYS_API_SECRET = os.getenv('CENSYS_API_SECRET', None)
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', None)
FOFA_API_KEY = os.getenv('FOFA_API_KEY', None)
FOFA_API_MAIL = os.getenv('FOFA_API_MAIL', None)

if CENSYS_API_SECRET and CENSYS_API_ID:
    censys_api = CensysHosts(api_id=CENSYS_API_ID, api_secret=CENSYS_API_SECRET)

if SHODAN_API_KEY:
    shodan_api = shodan.Shodan(SHODAN_API_KEY)

def query_zoomeye(squery):
    '''
    https://www.zoomeye.org/doc?channel=api
    '''
    findings = []
    if not ZOOMEYE_API_KEY:
        log.error("zoomeye: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("zoomeye: no query provided")
        return findings
    log.debug('zoomeye: querying %s', squery)
    try:
        results = requests.get('https://api.zoomeye.org/host/search',
                               params={'query': squery},
                               headers={'API-KEY': ZOOMEYE_API_KEY})
        results.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error('zoomeye: api error: %s', e)
        return findings
    results_data = results.json()
    total_results = results_data['total']
    log.info('zoomeye: found %s results for %s', total_results, squery)
    if total_results <= 20:
        for result in results_data['matches']:
            findings.append(result)
            log.info('zoomeye: found %s', result['ip'])
            log.debug('zoomeye: %s', result['portinfo']['banner'])
    else:
        log.warning('zoomeye: more than 20 results found. skipping query as it is not deemed rare.')
    return findings

def query_binaryedge(squery):
    findings = []
    if not BINARYEDGE_API_KEY:
        log.error("binaryedge: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("binaryedge: no query provided")
        return findings
    log.debug('binaryedge: querying %s', squery)
    try:
        results = requests.get('https://api.binaryedge.io/v2/query/search',
                               params={'query': squery},
                               headers={'X-Key': BINARYEDGE_API_KEY})
        results.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error('binaryedge: api error: %s', e)
        return findings
    results_data = results.json()
    total_results = results_data['total']
    log.info('binaryedge: found %s results for %s', total_results, squery)
    if total_results <= 20:
        for result in results_data['events']:
            findings.append(result)
            log.info('binaryedge: found %s', result['target']['ip'])
            if 'response' in result['result']['data']:
                log.debug('binaryedge: %s', result['result']['data']['response']['body']['content'])
            else:
                log.debug('binaryedge: response key not found in result')

    else:
        log.warning('binaryedge: more than 20 results found. skipping query as it is not deemed rare.')
    return findings

def query_censys(squery):
    findings = []
    if not (CENSYS_API_ID and CENSYS_API_SECRET):
        log.error("censys: without an api key queries are skipped")
        return findings
    try:
        log.debug('censys: querying %s', squery)
        results = censys_api.search(squery, per_page=30)
        total_results = len(results())
        log.info('censys: found %s results for %s', total_results, squery)
        if total_results == 0:
            log.warning('censys: no results found')
            return findings
        if total_results <= 20:
            for result in results():
                findings.append(result)
                log.info('censys: found %s', result['ip'])
        else:
            log.warning('censys: more than 20 results found. skipping query as it is not deemed rare.')
    except CensysException as ce:
        log.error('censys: api error: %s', ce)
    except Exception as e:
        log.error('censys: unexpected error: %s', e)
    return findings

def query_shodan(squery):
    findings = []
    if not SHODAN_API_KEY:
        log.error("shodan: without an api key queries are skipped")
        return findings
    if not squery:
        log.error("shodan: no query provided")
        return findings
    try:
        log.debug('shodan: querying %s', squery)
        results = shodan_api.search(squery)
        total_results = results['total']
        log.info('shodan: found %s results for %s', total_results, squery)
        if total_results <= 20:
            for result in results['matches']:
                findings.append(result)
                log.found('shodan: found %s', result['ip_str'])
                log.debug('shodan: %s', result['data'])
        else:
            log.warning('shodan: more than 20 results found. skipping query as it is not deemed rare.')
    except shodan.APIError as sae:
        log.error('shodan: api error: %s', sae)
    return findings

def query_fofa(squery):
    '''
    https://en.fofa.info/api
    '''
    findings = []
    if not FOFA_API_KEY or not FOFA_API_MAIL:
        log.error("fofa: without an api key and email queries are skipped")
        return findings
    if not squery:
        log.error("fofa: no query provided")
        return findings
    query64 = base64.b64encode(squery.encode('utf-8'))
    log.debug('fofa: querying %s (%s)', squery, query64)
    try:
        results = requests.get('https://fofa.info/api/v1/search/all',
                               params={
                                   'qbase64': query64,
                                   'fields': 'ip,port,banner',
                                   'size': 20,
                                   'page': 1,
                                   'key': FOFA_API_KEY,
                                   'email': FOFA_API_MAIL
                                }
        )
        results.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error('fofa: api error: %s', e)
        return findings
    results_data = results.json()
    if 'errmsg' in results_data:
        if '[820019]' in results_data['errmsg']:
            log.error('fofa: icon_hash queries are not supported on basic plans.')
            return findings
        log.error('fofa: unknown api error: %s', results_data['errmsg'])
        return findings
    total_results = results_data['size']
    log.info('fofa: found %s results for %s', total_results, squery)
    if total_results <= 20:
        for result in results_data['results']:
            findings.append(result)
            log.info('fofa: found ' + str(result[0]))
    else:
        log.warning('fofa: more than 20 results found. skipping query as it is not deemed rare.')
    return findings

def query_shodanindernetdb(ip):
    '''
    https://internetdb.shodan.io
    '''
    results = requests.get('https://internetdb.shodan.io/' + ip)
    if results.status_code != 200:
        log.error('shodanindernetdb: api error: %s - %s', results.status_code, results.text)
        return None
    results = results.json()
    if not results['ports']:
        log.warning('shodanindernetdb: no ports found')
    else:
        log.info('shodanindernetdb: found %s', results)
