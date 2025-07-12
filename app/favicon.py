#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mmh3
import base64
import codecs
import logging
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import app.getpage as getpage
import app.subprocessors as subprocessors

log = logging.getLogger(__name__)

def getmmh3(encodedfavicon):
    try:
        return mmh3.hash(encodedfavicon)
    except Exception as e:
        log.error("error calculating mmh3 hash: %s", e)
        return None

def getmd5(encodedfavicon):
    try:
        return hashlib.md5(encodedfavicon).hexdigest()
    except Exception as e:
        log.error("error calculating md5 hash: %s", e)
        return None

def commonhash(faviconmmh3):
    try:
        with open('common/favicon-hashes.txt', 'r', encoding='utf-8') as f:
            hashes = {int(line.rstrip()) for line in f}
        return faviconmmh3 in hashes
    except Exception as e:
        log.error("error checking common hash: %s", e)
        return False

def extract_favicon_url(domain, soup):
    try:
        icon_link = soup.find("link", rel=lambda x: x and x.lower() in ["shortcut icon", "icon"])
        if icon_link and icon_link["href"].startswith('data:image/'):
            favicon_str = icon_link["href"].split(',')[1]
            try:
                favicon64 = base64.b64decode(favicon_str)
                return favicon64, None
            except base64.binascii.Error:
                log.warning("Invalid base64 in inline favicon")
                return None, None
        elif icon_link:
            return None, urljoin(domain, icon_link["href"])
        return None, urljoin(domain, '/favicon.ico')
    except Exception as e:
        log.error("error extracting favicon URL: %s", e)
        return None, None

def get_favicon_data(location, usetor=True):
    try:
        favicondata = getpage.main(location, usetor=usetor)
        if favicondata and favicondata.status_code == 200:
            favicon64 = codecs.encode(favicondata.content, "base64")
            return favicon64
        log.info('favicon location (%s) returned no response or invalid status code', location)
    except Exception as e:
        log.error("error getting favicon data: %s", e)
    return None

def process_favicon(domain, requestobject, usetor=True):
    try:
        domain = domain.rstrip('/')
        soup = BeautifulSoup(requestobject.text, features="lxml")
        favicon64, location = extract_favicon_url(domain, soup)
        if not favicon64:
            favicon64 = get_favicon_data(location, usetor)

        if favicon64:
            faviconmmh3 = getmmh3(favicon64)
            faviconmd5 = getmd5(favicon64)
            log.info('favicon mmh3: %s, md5: %s', faviconmmh3, faviconmd5)
            return faviconmmh3, faviconmd5
        else:
            log.info('no favicon data found for %s', domain)
    except Exception as e:
        log.error("error processing favicon for %s: %s", domain, e)
    return None, None

def main(domain, requestobject, doshodan=True, usetor=True, docensys=True, dozoome=True, dofofa=True):
    faviconmmh3, faviconmd5 = process_favicon(domain, requestobject, usetor)
    if faviconmmh3 is None:
        return
    if commonhash(faviconmmh3):
        log.warning('favicon found in common hashlist, unlikely a unique asset - skipping shodan')
        return
    if doshodan is True:
        subprocessors.query_shodan('http.favicon.hash:' + str(faviconmmh3))
    if docensys is True:
        subprocessors.query_censys('services.http.response.favicons.md5_hash:' + str(faviconmd5))
    if dozoome is True:
        subprocessors.query_zoomeye('iconhash:' + str(faviconmmh3))
    if dofofa is True:
        subprocessors.query_fofa('icon_hash=' + str(faviconmmh3))
    return faviconmmh3
