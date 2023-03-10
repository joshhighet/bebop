#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import warnings
from bs4 import BeautifulSoup

import shodansearch
import censyssearch
import bedgesearch
import zoomeyesearch

log = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

common_titles = []
with open('common/http-titles.txt', 'r', encoding='utf-8') as common_titles_file:
    for line in common_titles_file:
        common_titles.append(line.strip())
    common_titles_file.close()

def main(requestobject, doshodan=True, docensys=True, dobedge=True, dozoome=True):
    if len(requestobject.text.splitlines()) == 1:
        log.error('single line response, not parsing')
        return None
    soup = BeautifulSoup(requestobject.text, 'html.parser')
    title = soup.find('title')
    if title is not None:
        log.info('title: %s', title.text)
        if title.text not in common_titles:
            if doshodan:
                shodansearch.query('http.title:"' + title.text + '"')
            if docensys:
                querystr = 'services.http.response.html_title:"' + title.text + '"'
                censyssearch.query(querystr)
            if dobedge:
                bedgesearch.query('web.title:"' + title.text + '"')
            if dozoome:
                zoomeyesearch.query('title:"' + title.text + '"')
        return title.text
    log.error('no title found on page')
    return None
