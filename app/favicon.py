#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mmh3
import codecs
import logging
from bs4 import BeautifulSoup

import getpage

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main(domain, requestobject):
    # if domain ends with a slash, remove it
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
    print('favicon location: {}'.format(location))
    favicondata = getpage.main(location)
    if favicondata.status_code != 200:
        print('favicon site returned status code {}'.format(favicondata.status_code))
        return faviconmmh3
    favicon64 = codecs.encode(favicondata.content,"base64")
    faviconmmh3 = mmh3.hash(favicon64)
    return faviconmmh3
