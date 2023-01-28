#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
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

logging.debug('fqdn: {}'.format(fqdn))
logging.debug('url: {}'.format(url))
logging.debug('url_base: {}'.format(url_base))

socksaddr = os.environ.get('SOCKS_HOST', 'host.docker.internal')
socksport = os.environ.get('SOCKS_PORT', 9050)
gen_chainconfig('telemetry.dark', socksport)

requestobject = getpage.main(args.target)
header_data = headers.main(requestobject)
print(header_data)
favicon_data = favicon.main(url_base, requestobject)
if favicon_data is not None:
    print('favicon mmh3: {}'.format(favicon_data))
    favicon_correlations = shodansearch.favicon(favicon_data)
    if len(favicon_correlations) > 50:
        logging.error('supressing - too many favicon correlations ({}).'.format(len(favicon_correlations)))
    if len(favicon_correlations) > 0:
        print('found {} favicon correlations'.format(len(favicon_correlations)))
        for correlation in favicon_correlations:
            print(correlation['ip_str'])
            print(correlation['data'])
if header_data['etag'] is not None:
    etag_correlations = shodansearch.general(header_data['etag'])
    if len(etag_correlations) > 0:
        print('found {} etag correlations'.format(len(etag_correlations)))
        for correlation in etag_correlations:
            print(correlation['ip_str'])
            print(correlation['data'])
pagespider_data = pagespider.main(args.target, requestobject)
for item in pagespider_data['internal']:
    opendir_data = opendir.main(getpage.main(item))
configcheck_data = configcheck.main(args.target)
title_data = title.main(requestobject)
torscan_data = torscan.main(fqdn)
