#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
return a list of all pages on a given site
'''
import re
import logging
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(url, siterequest):
    soup = BeautifulSoup(siterequest.content, 'html.parser')
    links = []
    external_links = []
    parsed_uri = urllib.parse.urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    for link in soup.find_all('a', href=True):
        if re.match("^http", link['href']):
            if not re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', link['href']):
                link_parsed = urllib.parse.urlparse(link['href'])
                link_domain = link_parsed.netloc
                if domain in link['href'] or (link_domain.startswith("www.") and link_domain[4:] == domain[4:]):
                    loggiing.info('link: ' + link['href'])
                    links.append(link['href'])
                else:
                    logging.info('external link: ' + link['href'])
                    external_links.append(link['href'])
        else:
            links.append(urljoin(url,link['href']))
    if not links:
        logging.debug('did not find any internal links')
    if not external_links:
        logging.debug('did not find any external links')
    dedup_links = list(set(links))
    dedup_external_links = list(set(external_links))
    return {'internal': dedup_links, 'external': dedup_external_links}
