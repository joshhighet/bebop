#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mmh3
import codecs
import logging
from bs4 import BeautifulSoup

import getpage

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(domain, requestobject):
    domain = domain.rstrip('/')
    faviconmmh3 = None
    if 'http' not in domain:
        domain = 'http://' + domain
    soup = BeautifulSoup(requestobject.text, features="lxml")
    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="icon")
    if icon_link is None:
        location = domain + '/favicon.ico'
    else:
        location = icon_link["href"]
    if 'http' not in location:
        location = domain + location
    if 'image/x-icon' not in location:
        favicondata = getpage.main(location)
        if favicondata is None:
            logging.info('favicon site ({}) returned no response'.format(location))
            return faviconmmh3
        if favicondata.status_code != 200:
            logging.info('favicon site ({}) returned status code {}'.format(location, favicondata.status_code))
            return faviconmmh3
        logging.info('favicon location: {}'.format(location))
        favicon64 = codecs.encode(favicondata.content,"base64")
    else:
        logging.info('favicon is encoded in html')
        favicon64 = location[22:]
        logging.debug('favicon64: {}'.format(favicon64))
    faviconmmh3 = mmh3.hash(favicon64)
    logging.info('favicon mmh3: {}'.format(faviconmmh3))
    return faviconmmh3
