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
from utilities import preflight, getfqdn, getbaseurl, gen_chainconfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target address')
args = parser.parse_args()

preflight()
url = args.target
fqdn = getfqdn(url)
url_base = getbaseurl(url)

requestobject = getpage.main(args.target)
if requestobject is None:
    logging.error('failed to retrieve page')
    sys.exit(1)
if requestobject.status_code >= 400:
    logging.warning('unexpected response code: %s', requestobject.status_code)
title.main(requestobject)
header_data = headers.main(requestobject)
if header_data['etag'] is not None:
    etag_correlations = shodansearch.query(header_data['etag'])
favicon_data = favicon.main(url_base, requestobject)
configcheck.main(args.target)
torscan.main(fqdn)
pagespider_data = pagespider.main(args.target, requestobject)
for item in pagespider_data['internal']:
    itemsource = getpage.main(item)
    if itemsource is not None:
        opendir.main(itemsource)
