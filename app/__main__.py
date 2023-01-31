#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import argparse

import getpage
import headers
import favicon
import pagespider
import title
import portscan
import configcheck
import opendir
import shodansearch
import getcert
import cliart
from utilities import preflight, getfqdn, getbaseurl, gen_chainconfig, validurl

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target address')
parser.add_argument('--loglevel', 
                    help='set logging level', 
                    default='CRITICAL', 
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
parser.add_argument('--nosocks', 
                    help='route traffic over clearnet (no tor)', 
                    action='store_true', 
                    default=False)
parser.add_argument('--useragent', 
                    help='set user-agent', 
                    default='Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0')
args = parser.parse_args()

logging.basicConfig(
    level=logging.getLevelName(args.loglevel),
    format='%(asctime)-11s %(levelname)-8s %(filename)-15s %(funcName)-20s %(message)s',
    datefmt="%I:%M:%S%p",
)

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

preflight()
cliart.prints()
if args.nosocks is True:
    usrip = getpage.main('https://ipinfo.io/ip')
    if usrip.status_code == 200:
        logging.critical('clearnet traffic enabled.. (hello %s)', usrip.text)
if not validurl(args.target):
    if validurl('http://' + args.target):
        logging.warning('no protocol found, appending http:// to target')
        args.target = 'http://' + args.target
    else:
        logging.critical('failed to parse url - ensure a protocol is specified')
        sys.exit(1)
fqdn = getfqdn(args.target)
url_base = getbaseurl(args.target)
print('fqdn: %s' % fqdn)
if url_base == args.target:
    print('target/base url: %s' % args.target)
else:
    print('base url: %s' % url_base)
    print('target: %s' % args.target)
requestobject = getpage.main(args.target, usetor=args.nosocks)
if requestobject is None:
    logging.error('failed to retrieve page')
    sys.exit(1)
if requestobject.status_code != 200:
    logging.warning('unexpected response code: %s', requestobject.status_code)
title.main(requestobject)
header_data = headers.main(requestobject)
configcheck.main(args.target)
if args.target.startswith('https'):
    getcert_data = getcert.main(args.target)
pagespider_data = pagespider.main(args.target, requestobject)
favicon_data = favicon.main(url_base, requestobject)
for item in pagespider_data['internal']:
    logging.info('scanning %s', item)
    itemsource = getpage.main(item)
    if itemsource is not None:
        opendir.main(itemsource)
portscan.main(fqdn, useragent=args.useragent, usetor=args.nosocks)
