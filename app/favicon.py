#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mmh3
import codecs
import logging
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import getpage
import subprocessors

log = logging.getLogger(__name__)

def getmmh3(encodedfavicon):
    return mmh3.hash(encodedfavicon)

def getmd5(encodedfavicon):
    return hashlib.md5(encodedfavicon).hexdigest()

def commonhash(faviconmmh3):
    with open('common/favicon-hashes.txt', 'r', encoding='utf-8') as f:
        hashes = {int(line.rstrip()) for line in f}
    return faviconmmh3 in hashes

def getfavicon64(domain, requestobject, usetor=True):
    domain = domain.rstrip('/')
    soup = BeautifulSoup(requestobject.text, features="lxml")
    icon_link = soup.find("link", rel=lambda x: x and x.lower() in ["shortcut icon", "icon"])
    if icon_link is None:
        location = urljoin(domain, '/favicon.ico')
    elif icon_link["href"].startswith('data:image/'):
        favicon64 = icon_link["href"].split(',')[1]
        return favicon64
    else:
        location = urljoin(domain, icon_link["href"])
    log.debug('i think the favicon location is: %s', location)
    favicondata = getpage.main(location, usetor=usetor)
    if favicondata is None or favicondata.status_code != 200:
        log.info('favicon location (%s) returned no response or invalid status code', location)
        return None
    favicon64 = codecs.encode(favicondata.content, "base64")
    return favicon64

def main(domain, requestobject, doshodan=True, usetor=True, docensys=True, dobedge=True, dozoome=True):
    favicon64 = getfavicon64(domain, requestobject, usetor=usetor)
    if favicon64 is None:
        return None
    faviconmmh3 = getmmh3(favicon64)
    faviconmd5 = getmd5(favicon64)
    log.info('favicon mmh3: %s', faviconmmh3)
    if commonhash(faviconmmh3):
        log.warn('favicon found in common hashlist, unlikely a unique asset - skipping shodan')
        direct_url = f'https://www.shodan.io/search?query=http.favicon.hash%3A{faviconmmh3}'
        log.debug(direct_url)
        return faviconmmh3
    if doshodan is True:
        subprocessors.query_shodan('http.favicon.hash:' + str(faviconmmh3))
    if docensys is True:
        subprocessors.query_censys('services.http.response.favicons.md5_hash:' + str(faviconmd5))
    if dobedge is True:
        subprocessors.query_binaryedge('web.favicon.mmh3:' + str(faviconmmh3))
    if dozoome is True:
        subprocessors.query_zoomeye('iconhash:' + str(faviconmmh3))
    return faviconmmh3
