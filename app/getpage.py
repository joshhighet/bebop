#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
requests and returns a request object
'''
import sys
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
    logging.info('making request to: {} - tor:{}'.format(weblocation, usetor))
    try:
        siterequest = requests.get(
            weblocation,
            proxies=reqproxies,
            verify=False,
            timeout=30
        )
        logging.info('request took: {} seconds'.format(siterequest.elapsed.total_seconds()))
    except requests.exceptions.ConnectionError as rece:
        logging.error(rece)
        return None
    except requests.exceptions.Timeout as ret:
        logging.error(ret)
        return None
    except Exception as gene:
        logging.critical('unknown error: {}'.format(gene))
        sys.exit(1)
    return siterequest
