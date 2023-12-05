#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import asyncio
import argparse

import app.getpage as getpage
import app.headers as headers
import app.favicon as favicon
import app.pagespider as pagespider
import app.title as title
import app.portscan as portscan
import app.configcheck as configcheck
import app.opendir as opendir
import app.getcert as getcert
import app.cliart as cliart
from .utilities import preflight, getfqdn, getbaseurl, validurl, getport

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target address')
parser.add_argument('--loglevel',
                    help='set logging level',
                    default='INFO',
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
parser.add_argument('--clearnet',
                    help='route traffic over clearnet (no tor)',
                    action='store_true',
                    default=False)
parser.add_argument('--useragent',
                    help='set user-agent',
                    default='Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0')
args = parser.parse_args()

logging.basicConfig(
    level=logging.getLevelName(args.loglevel),
    format='%(asctime)-11s %(levelname)-8s %(lineno)d:%(filename)-15s %(funcName)-25s %(message)s',
    datefmt="%I:%M:%S%p",
)

if len(sys.argv) == 1:
    print(
    '''
                __                     
        _(\    |@@|                        __         __              
        (__/\__ \--/ __                    / /_  ___  / /_  ____  ____ 
            \___|----|  |   __             / __ \/ _ \/ __ \/ __ \/ __ \\
                \ }{ /\ )_ / _\           / /_/ /  __/ /_/ / /_/ / /_/ /
                /\__/\ \__O (__          /_.___/\___/_.___/\____/ .___/ 
            (--/\--)    \__/                                /_/      
            _)(  )(_                  
            `---''---`                 hidden service safari 👀 🧅 💻 
    ''')

cliart.prints()

if args.clearnet is True:
    logging.critical('clearnet routing enabled..')
    torstate = False
else:
    logging.debug('tor routing enabled..')
    torstate = True
    preflight()

if not validurl(args.target):
    if validurl('http://' + args.target):
        args.target = 'http://' + args.target
        logging.warning('no protocol provided, appending (now: %s)', args.target)
    else:
        logging.critical('failed to parse url - ensure a protocol is specified')
        sys.exit(1)
fqdn = getfqdn(args.target)
if fqdn.endswith('.onion'):
    if torstate is False:
        logging.critical('you cannot disable tor routing if your target is a .onion service!')
        sys.exit(1)
url_base = getbaseurl(args.target)
logging.debug('target: %s url_base: %s fqdn: %s', args.target, url_base, fqdn)
requestobject = getpage.main(args.target, usetor=torstate)
if requestobject is None:
    logging.error('failed to retrieve page')
    sys.exit(1)
if requestobject.status_code != 200:
    logging.warning('unexpected response code: %s', requestobject.status_code)
if args.target.startswith('https'):
    targetport = getport(args.target)
    getcert_data = getcert.main(fqdn, port=targetport)
title.main(requestobject)
header_data = headers.main(requestobject)
loop = asyncio.get_event_loop()
loop.run_until_complete(configcheck.main(args.target, usetor=torstate))
loop.close()
favicon_data = favicon.main(url_base, requestobject, usetor=torstate)
pagespider_data = pagespider.main(requestobject, usetor=torstate, skip_queryurl=True)
for item in pagespider_data['samedomain']:
    itemsource = getpage.main(item)
    if itemsource is not None:
        opendir.main(itemsource)
portscan.main(fqdn, useragent=args.useragent, usetor=torstate)
