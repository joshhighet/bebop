#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
import urllib.parse
import requests
from bs4 import BeautifulSoup

from .utilities import getsocks, useragentstr

log = logging.getLogger(__name__)

def get_links(soup, base_url):
    links = [link['href'] for link in soup.find_all('a', href=True)]
    dedup_links = list(set(links))
    same_domain_links = []
    diff_domain_links = []
    emails = []
    protocol = 'https:' if base_url.scheme == 'https' else 'http:'
    for link in dedup_links:
        log.debug('found link: %s', link)
        if link.startswith('//'):
            link = protocol + link
        parsed_link = urllib.parse.urlparse(link)
        if link.startswith('mailto:'):
            emails.append(link.replace('mailto:', ''))
        elif parsed_link.netloc == base_url.netloc or parsed_link.netloc == '':
            if parsed_link.netloc == '':
                link = urllib.parse.urljoin(base_url.geturl(), link)
            same_domain_links.append(link)
        elif parsed_link.netloc and parsed_link.netloc != base_url.netloc:
            diff_domain_links.append(link)
    return {
        'samedomain': same_domain_links,
        'extdomain': diff_domain_links,
        'emails': emails
    }

def main(siterequest, usetor, skip_queryurl):
    soup = BeautifulSoup(siterequest.content, 'html.parser')
    url = siterequest.url
    if skip_queryurl and '?' in url:
        log.error('this looks like a query url - skipping spider: %s', url)
        return None
    base_url = urllib.parse.urlparse(url)
    results = get_links(soup, base_url)
    log.info('found %s total links', sum(len(lst) for lst in results.values()))
    return results
