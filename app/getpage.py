#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import requests

from utilities import getsocks

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
requests.packages.urllib3.disable_warnings()

def main(weblocation, usetor=True):
    if usetor:
        reqproxies = getsocks()
    else:
        reqproxies = None
    logging.debug('making request to: %s - tor:%s', weblocation, usetor)
    try:
        siterequest = requests.get(
            weblocation,
            proxies=reqproxies,
            verify=False,
            timeout=30
        )
        logging.debug('request took: %s seconds', siterequest.elapsed.total_seconds())
    except requests.exceptions.ConnectionError as rece:
        logging.error(rece)
        return None
    except requests.exceptions.Timeout as ret:
        logging.error(ret)
        return None
    return siterequest
