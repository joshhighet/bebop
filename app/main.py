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
import torscan
import configcheck
import opendir
import shodansearch
import getcert
from utilities import preflight, getfqdn, getbaseurl, gen_chainconfig, validurl

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target address')
args = parser.parse_args()

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
if not validurl(args.target):
    logging.critical('failed to parse url - ensure a protocol is specified')
    sys.exit(1)
fqdn = getfqdn(args.target)
url_base = getbaseurl(args.target)
requestobject = getpage.main(args.target)
if requestobject is None:
    logging.error('failed to retrieve page')
    sys.exit(1)
if requestobject.status_code != 200:
    logging.warning('unexpected response code: %s', requestobject.status_code)
title.main(requestobject)
header_data = headers.main(requestobject)
if args.target.startswith('https'):
    getcert_data = getcert.main(args.target)
pagespider_data = pagespider.main(args.target, requestobject)
configcheck.main(args.target)
favicon_data = favicon.main(url_base, requestobject)
for item in pagespider_data['internal']:
    itemsource = getpage.main(item)
    if itemsource is not None:
        opendir.main(itemsource)
torscan.main(fqdn)