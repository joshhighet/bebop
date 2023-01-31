#!/usr/bin/env python3
# https://raw.githubusercontent.com/joshhighet/bebop/main/assets/pagespider-test.html
import re
import logging
import requests

log = logging.getLogger(__name__)

rex = {
    'btc': re.compile(r'(bc1q[A-Za-z0-9]{39})|(([13]|bc1)[A-HJ-NP-Za-km-z1-9]{27,34}(?![A-Za-z0-9]))'),
    'xmr': re.compile(r'([0-9AB]{1})([0-9a-zA-Z]{93})'),
    'eth': re.compile(r'0x[a-fA-F0-9]{40}')
}

def getwallet_data(wallet, chain='btc'):
    url = 'https://api.blockcypher.com/v1/%s/main/addrs/%s/balance' % (chain, wallet)
    data = requests.get(url)
    if data.status_code == 200:
        log.info('found %s wallet with balance %s (%s)', chain, data.json()['final_balance'], wallet)
        return data.json()
    log.error('%s: failed to retrieve data about %s - likely a false match', chain, wallet)
    return None

def main(sitesource):
    findings = {key: [] for key in rex.keys()}
    for currency, pattern in rex.items():
        for match in re.finditer(pattern, sitesource):
            findings[currency].append(match.group())
    for currency, values in findings.items():
        findings[currency] = list(set(values))
        for value in findings[currency]:
            log.debug('found a potential %s wallet: %s', currency, value)
            if currency == 'btc':
                getwallet_data(value)
            elif currency == 'eth':
                getwallet_data(value, 'eth')
            else:
                log.info('found suspected %s wallet: %s', currency, value)
    return findings
