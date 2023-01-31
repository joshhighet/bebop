#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import requests

from utilities import getsocks

log = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings()

def main(weblocation, usetor=True):
    if usetor:
        reqproxies = getsocks()
    else:
        reqproxies = None
    log.debug('making request to: %s - tor:%s', weblocation, usetor)
    try:
        siterequest = requests.get(
            weblocation,
            proxies=reqproxies,
            verify=False,
            timeout=30,
            allow_redirects=True
        )
        if siterequest.history:
            log.warning('request was redirected to: %s', siterequest.url)
        log.debug('request took: %s seconds', siterequest.elapsed.total_seconds())
    except requests.exceptions.ConnectionError as rece:
        log.error(rece)
        return None
    except requests.exceptions.Timeout as ret:
        log.error(ret)
        return None
    return siterequest
