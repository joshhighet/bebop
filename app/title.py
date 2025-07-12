#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import warnings
from bs4 import BeautifulSoup

import app.subprocessors as subprocessors

log = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

common_titles = []
with open('common/http-titles.txt', 'r', encoding='utf-8') as common_titles_file:
    for line in common_titles_file:
        common_titles.append(line.strip())
    common_titles_file.close()

def main(requestobject, doshodan=True, docensys=True, dozoome=True, dofofa=True):
    soup = BeautifulSoup(requestobject.text, 'html.parser')
    title = soup.find('title')
    if title is not None:
        log.info('title: %s', title.text)
        if title.text not in common_titles and len(title.text) > 0:
            if doshodan:
                subprocessors.query_shodan('http.title:"' + title.text + '"')
            if docensys:
                querystr = 'services.http.response.html_title:"' + title.text + '"'
                subprocessors.query_censys(querystr)
            if dozoome:
                subprocessors.query_zoomeye('title:"' + title.text + '"')
            if dofofa:
                subprocessors.query_fofa('title=' + str(title.text))
        return title.text
    log.warning('failed to extract title from %s', requestobject.url)
    return None
