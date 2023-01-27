#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
requests and returns a request object
'''
import sys
import logging
import requests

from utilities import getsocks, checktcp

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
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
            timeout=30
        )
    except requests.exceptions.ConnectionError as rece:
        logging.error(rece)
    except requests.exceptions.Timeout as ret:
        logging.error(ret)
    except Exception as gene:
        logging.critical('unknown error: {}'.format(gene))
        sys.exit(1)
    return siterequest
