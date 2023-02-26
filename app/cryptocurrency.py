#!/usr/bin/env python3
# https://raw.githubusercontent.com/joshhighet/bebop/main/assets/pagespider-test.html
import re
import logging
from bs4 import BeautifulSoup
import getpage
import requests

log = logging.getLogger(__name__)

rex = {
    'btc': re.compile(r'(bc1q[A-Za-z0-9]{39})|(([13]|bc1)[A-HJ-NP-Za-km-z1-9]{27,34}(?![A-Za-z0-9]))'),
    'xmr': re.compile(r'([0-9AB]{1})([0-9a-zA-Z]{93})'),
    'eth': re.compile(r'0x[a-fA-F0-9]{40}')
}

def getwallet_data(wallet, chain='btc'):
    url = 'https://api.blockcypher.com/v1/%s/main/addrs/%s/balance' % (chain, wallet)
    data = getpage.main(url)
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

def walletexplorer_inspect_and_pivot(address):
    walletid = ""
    addresses = []
    try:
        ##walletnote
        addresswe = f"https://www.walletexplorer.com/address/{address}"
        pageaddr = requests.get(addresswe)
        soup = BeautifulSoup(pageaddr.text, 'html.parser')
        linkwallet = soup.find("div", {"class": "walletnote"}).find('a').get('href')
        walletid =  linkwallet.split("/")
        if(len(walletid)>0):
            urlwalletaddress = f"https://www.walletexplorer.com/wallet/{walletid[2]}/addresses"
            walletaddr = requests.get(urlwalletaddress)
            soup = BeautifulSoup(walletaddr.text, 'html.parser')
            addresstable = soup.find("table")
            trs = addresstable.find_all('tr')
            first = True
            for tr in trs:
                if not first:
                    pivotaddress = tr.find("a").get("href").replace("/address/","")
                    if pivotaddress != address:
                        addresses.append(pivotaddress)
                first = False
    except Exception as exx:
        log.error('%s: failed to retrieve data about %s - likely a false match', exx, address)
    return walletid, addresses
