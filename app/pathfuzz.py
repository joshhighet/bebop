#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import urllib3

from utilities import getsocks, useragentstr

log = logging.getLogger(__name__)

def main(target, usetor=True):
    with open('assets/fuzz-wordlist.txt') as f:
        urls = [line.rstrip() for line in f]
    with requests.Session() as session:
        for url in urls:
            fetchtgt = target + '/' + url
            try:
                response = session.get(
                    fetchtgt,
                    proxies=getsocks(),
                    verify=False,
                    timeout=30,
                    allow_redirects=False,
                    headers={'User-Agent': useragentstr}
                )
            except requests.exceptions.ConnectionError as rece:
                log.error(rece)
            except requests.exceptions.Timeout as ret:
                log.error(ret)
            except urllib3.exceptions.MaxRetryError as urle:
                if 'General SOCKS server failure' in urle:
                    log.error('proxy timeout!')
                log.critical(urle)
            if '404' and 'Page not found' in response.text:
                log.debug('this page looks like a 404 w/ the wrong status code!')
                continue
            if response.status_code == 200:
                log.info('found %s', fetchtgt)
