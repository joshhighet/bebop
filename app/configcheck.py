#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests

log = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings()

import title
from utilities import getsocks, useragentstr

interesting_paths = [
    {'uri': '/server-status', 'code': 200, 'text': 'Apache'},
    {'uri': '/server-info', 'code': 200, 'text': 'Apache'},
    {'uri': '/robots.txt', 'code': 200, 'text': None},
    {'uri': '/sitemap.xml', 'code': 200, 'text': None},
    {'uri': '/wp-login.php', 'code': 200, 'text': 'login'},
    {'uri': '/xmlrpc.php', 'code': 405, 'text': 'XML-RPC server accepts POST requests only'}
]

def main(location, usetor=True):
    if location.endswith('/'):
        location = location[:-1]
    if usetor:
        reqproxies = getsocks()
    else:
        reqproxies = None
    logging.debug('requesting: %s - usetor:%s', location, usetor)
    logging.debug('using proxies: %s', reqproxies)
    with requests.Session() as session:
        for path in interesting_paths:
            uri = location + path['uri']
            log.info('scanning %s - expecting %s', uri, path['code'])
            try:
                response = session.get(
                    uri,
                    proxies=reqproxies,
                    verify=False,
                    timeout=30,
                    allow_redirects=True,
                    headers={'User-Agent': useragentstr}
                    )
            except requests.exceptions.ConnectionError as rece:
                log.error(rece)
            except requests.exceptions.Timeout as ret:
                log.error(ret)
            if '404' and 'Page not found' in response.text:
                log.debug('this page looks like a 404 w/ the wrong status code!')
                continue
            if response.status_code == path['code']:
                title.main(response)
                if path['text'] is None:
                    log.info(f'found {path["code"]} at {uri}')
                elif path['text'] in response.text:
                    log.info(f'found {path["code"]} at {uri}')
                else:
                    log.debug(f'found {path["code"]} at {uri} but no match for {path["text"]}')
            else:
                log.debug(f'found {response.status_code} at {uri}')
