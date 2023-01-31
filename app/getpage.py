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
    try:
        siterequest = requests.get(
            weblocation,
            proxies=reqproxies,
            verify=False,
            timeout=30,
            allow_redirects=True
        )
        if siterequest.history:
            for resp in siterequest.history:
                log.info('redirect: %s (%s)', resp.url, resp.status_code)
            log.info("followed to: %s", siterequest.url)
        log.debug('request took: %s seconds', siterequest.elapsed.total_seconds())
    except requests.exceptions.ConnectionError as rece:
        log.error(rece)
        return None
    except requests.exceptions.Timeout as ret:
        log.error(ret)
        return None
    return siterequest
