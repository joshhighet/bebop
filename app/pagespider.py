#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import cryptocurrency

log = logging.getLogger(__name__)

def main(url, siterequest, skip_queryurl=True):
    cryptocurrency.main(siterequest.text)
    if skip_queryurl and '?' in url:
        log.error('this looks like a query url - skipping spider: %s', url)
        return None
    soup = BeautifulSoup(siterequest.content, 'html.parser')
    parsed_base_uri = urllib.parse.urlparse(url)
    links = []
    for link in soup.find_all('a', href=True):
        links.append(link['href'])
    dedup_links = list(set(links))
    emails = []
    internal_links = []
    external_links = []
    external_onionlinks = []
    subdomain_links = []
    for link in dedup_links:
        parsed_link = urllib.parse.urlparse(link)
        if link.startswith('mailto:'):
            email = link.replace('mailto:', '')
            log.info('found email: %s', email)
            emails.append(email)
        elif parsed_link.netloc == parsed_base_uri.netloc:
            internal_links.append(link)
        elif parsed_link.netloc == '':
            internal_links.append(urljoin(url, link))
        elif parsed_link.netloc.endswith(parsed_base_uri.netloc):
            subdomain_links.append(link)
        elif parsed_link.netloc.endswith('.onion'):
            external_onionlinks.append(link)
        else:
            external_links.append(link)
    onion_domains = []
    for link in external_onionlinks:
        parsed_link = urllib.parse.urlparse(link)
        onion_domains.append(parsed_link.netloc)
    onion_domains = list(set(onion_domains))
    if len(onion_domains) > 0:
        log.info('found %s external onion links across %s domains', len(external_onionlinks), len(onion_domains))
        for domain in onion_domains:
            log.info('domain: %s', domain)
    else:
        log.debug('no external onion links found')
    if len(subdomain_links) > 0:
        log.info('found %s subdomain links', len(subdomain_links))
    else:
        log.debug('no subdomain links found')
    if len(external_links) > 0:
        log.info('found %s external links', len(external_links))
    else:
        log.debug('no external links found')
    if len(internal_links) > 0:
        log.info('found %s internal links', len(internal_links))
    else:
        log.debug('no internal links found')
    if len(emails) > 0:
        log.info('found %s emails', len(emails))
    else:
        log.debug('no emails found')

    return {
        'emails': emails,
        'internal': internal_links,
        'external': external_links,
        'external_onion': external_onionlinks,
        'subdomains': subdomain_links,
        'onion_domains': onion_domains
    }
