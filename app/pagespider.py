#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
import urllib.parse
import requests
from bs4 import BeautifulSoup

from utilities import getsocks, useragentstr

import cryptocurrency

log = logging.getLogger(__name__)

def get_links(soup, base_url):
    links = [link['href'] for link in soup.find_all('a', href=True)]
    dedup_links = list(set(links))
    internal_links = []
    external_links = []
    subdomain_links = []
    external_onionlinks = []
    for link in dedup_links:
        parsed_link = urllib.parse.urlparse(link)
        if link.startswith('mailto:'):
            email = link.replace('mailto:', '')
            log.info('found email: %s', email)
            yield 'email', email
        elif parsed_link.netloc == base_url.netloc:
            internal_links.append(link)
        elif parsed_link.netloc == '':
            internal_links.append(urllib.parse.urljoin(base_url.geturl(), link))
        elif parsed_link.netloc.endswith(base_url.netloc):
            subdomain_links.append(link)
        elif parsed_link.netloc.endswith('.onion'):
            external_onionlinks.append(link)
        else:
            external_links.append(link)
    onion_domains = set(parsed_link.netloc for link in external_onionlinks)
    if onion_domains:
        log.info('found %s external onion links across %s domains', len(external_onionlinks), len(onion_domains))
        for domain in onion_domains:
            log.info('domain: %s', domain)
    else:
        log.debug('no external onion links found')
    if subdomain_links:
        log.info('found %s subdomain links', len(subdomain_links))
    else:
        log.debug('no subdomain links found')
    if external_links:
        log.info('found %s external links', len(external_links))
    else:
        log.debug('no external links found')
    if internal_links:
        log.info('found %s internal links', len(internal_links))
    else:
        log.debug('no internal links found')
    if external_onionlinks:
        log.info('found %s external onion links', len(external_onionlinks))
    else:
        log.debug('no external onion links found')
    yield 'internal', internal_links
    yield 'external', external_links
    yield 'subdomains', subdomain_links
    yield 'external_onion', external_onionlinks
    yield 'onion_domains', list(onion_domains)


def main(url, siterequest, skip_queryurl=True, usetor=True):
    if usetor:
        reqproxies = getsocks()
    else:
        reqproxies = None
    with requests.Session() as session:
        response = session.get(
            url,
            proxies=reqproxies,
            verify=False,
            timeout=30,
            allow_redirects=True,
            headers={'User-Agent': useragentstr}
            )
        cryptocurrency.main(response.text)
        if skip_queryurl and '?' in url:
            log.error('this looks like a query url - skipping spider: %s', url)
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = urllib.parse.urlparse(url)
        results = {name: data for name, data in get_links(soup, base_url)}
        log.info('found %s total links', sum(map(len, results.values())))
        return results
