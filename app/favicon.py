#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mmh3
import codecs
import logging
from bs4 import BeautifulSoup

import getpage
import shodansearch

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def getmmh3(encodedfavicon):
    return mmh3.hash(encodedfavicon)

def commonhash(faviconmmh3):
    with open('common/favicon-hashes.txt', 'r', encoding='utf-8') as f:
        hashes = {int(line.rstrip()) for line in f}
    if faviconmmh3 in hashes:
        return True
    return False

def getfavicon64(domain, requestobject):
    domain = domain.rstrip('/')
    soup = BeautifulSoup(requestobject.text, features="lxml")
    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="icon")
    if icon_link is None:
        location = domain + '/favicon.ico'
    else:
        location = icon_link["href"]
        if icon_link["href"].startswith('data:image/'):
            favicon64 = icon_link["href"].split(',')[1]
            return favicon64
    if not location.startswith('http'):
        location = domain + location
    logging.info('favicon location: %s', location)
    favicondata = getpage.main(location)
    if favicondata is None:
        logging.info('favicon location (%s) returned no response', location)
        return None
    if favicondata.status_code != 200:
        logging.info('favicon location (%s) returned status code %s', \
            location, favicondata.status_code)
        return None
    favicon64 = codecs.encode(favicondata.content,"base64")
    return favicon64

def main(domain, requestobject, doshodan=True):
    favicon64 = getfavicon64(domain, requestobject)
    if favicon64 is None:
        return None
    faviconmmh3 = getmmh3(favicon64)
    logging.info('favicon mmh3: %s', faviconmmh3)
    if commonhash(faviconmmh3) is True:
        logging.warn('favicon found in common hashlist, unlikely a unique asset - skipping shodan')
        direct_url = 'https://www.shodan.io/search?query=http.favicon.hash%3A' + str(faviconmmh3)
        logging.debug(direct_url)
        return faviconmmh3
    if doshodan is True:
        shodansearch.query('http.favicon.hash:' + faviconmmh3)
    return faviconmmh3
