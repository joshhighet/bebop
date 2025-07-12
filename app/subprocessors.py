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

FOFA_API_KEY = os.getenv('FOFA_API_KEY', None)
CENSYS_API_ID = os.getenv('CENSYS_API_ID', None)
FOFA_API_MAIL = os.getenv('FOFA_API_MAIL', None)
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', None)
URLSCAN_API_KEY = os.getenv('URLSCAN_API_KEY', None)
ZOOMEYE_API_KEY = os.getenv('ZOOMEYE_API_KEY', None)
CENSYS_API_SECRET = os.getenv('CENSYS_API_SECRET', None)
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', None)
SECURITYTRAILS_API_KEY = os.getenv('SECURITYTRAILS_API_KEY', None)

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
        log.warning("zoomeye: without an api key queries are skipped")
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

def query_censys(squery):
    findings = []
    if not (CENSYS_API_ID and CENSYS_API_SECRET):
        log.warning("censys: without an api key queries are skipped")
        return findings
    try:
        log.debug('censys: querying %s', squery)
        results = censys_api.search(squery, per_page=30)
        total_results = len(results())
        log.info('censys: found %s results for %s', total_results, squery)
        if total_results == 0:
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
        log.warning("shodan: without an api key queries are skipped")
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
                log.info('shodan: found %s', result['ip_str'])
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
        log.warning("fofa: without an api key and email queries are skipped")
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

def query_resolutions_securitytrails(ip_address):
    if not SECURITYTRAILS_API_KEY:
        log.warning("securitytrails: without an api key queries are skipped")
        return set()
    url = f"https://api.securitytrails.com/v1/ips/nearby/{ip_address}"
    headers = {"apikey": SECURITYTRAILS_API_KEY}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        logging.error(f"unhandled error: {response.status_code} - {response.text}")
        return set()
    data = response.json()
    hostnames = set()
    for block in data.get("blocks", []):
        for hostname in block.get("hostnames", []):
            hostnames.add(hostname)
    logging.info(f"found {len(hostnames)} hostnames on SecurityTrails")
    return hostnames

def query_resolutions_virustotal(ip_address):
    if not VIRUSTOTAL_API_KEY:
        log.warning("virustotal: without an api key queries are skipped")
        return set()
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}/resolutions"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        hostnames = set()
        if 'data' in data:
            for item in data['data']:
                if 'attributes' in item and 'host_name' in item['attributes']:
                    hostnames.add(item['attributes']['host_name'])
        logging.info(f"found {len(hostnames)} hostnames on VirusTotal")
        return hostnames
    except requests.RequestException as e:
        logging.error(f"VirusTotal API error: {e}")
        return set()
    except (KeyError, TypeError) as e:
        logging.error(f"Unexpected response structure from VirusTotal: {e}")
        return set()

def query_resolutions_urlscan(ip_address):
    if not URLSCAN_API_KEY:
        log.warning("urlscan: without an api key queries are skipped")
        return set()
    search_url = f'https://urlscan.io/api/v1/search/?q=ip:"{ip_address}"'
    headers = {
        'API-Key': URLSCAN_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.get(search_url, headers=headers, timeout=10)
    if response.status_code != 200:
        logging.error(f"unhandled error: {response.status_code} - {response.text}")
        return set()
    data = response.json()
    hostnames = set()
    for item in data.get('results', []):
        if 'task' in item and 'domain' in item['task']:
            hostnames.add(item['task']['domain'])
    logging.info(f"found {len(hostnames)} hostnames on urlscan.io")
    return hostnames
