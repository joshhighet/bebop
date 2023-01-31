#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import cryptocurrency

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(url, siterequest, skip_queryurl=True):
    cryptocurrency.main(siterequest.text)
    if skip_queryurl and '?' in url:
        logging.error('this looks like a query url - skipping spider: %s', url)
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
            logging.info('found email: %s', email)
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
    logging.info('found %s emails', len(emails))
    logging.info('found %s internal links', len(internal_links))
    logging.info('found %s external links', len(external_links))
    logging.info('found %s subdomain links', len(subdomain_links))
    logging.info('found %s external onion links across %s domains', len(external_onionlinks), len(onion_domains))
    for domain in onion_domains:
        logging.info('domain: %s', domain)
    return {
        'emails': emails,
        'internal': internal_links,
        'external': external_links,
        'external_onion': external_onionlinks,
        'subdomains': subdomain_links,
        'onion_domains': onion_domains
    }
