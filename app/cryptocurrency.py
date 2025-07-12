#!/usr/bin/env python3
import re
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

rex = {
    'btc': re.compile(r'\b(bc1[ac-hj-np-z02-9]{39,59}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b'),
    'xmr': re.compile(r'([0-9AB]{1})([0-9a-zA-Z]{93})'),
    'eth': re.compile(r'0x[a-fA-F0-9]{40}')
}

def getwallet_data(wallet, chain='btc'):
    url = 'https://api.blockcypher.com/v1/%s/main/addrs/%s/balance' % (chain, wallet)
    data = requests.get(url, timeout=10)
    if data.status_code == 200:
        bal = data.json()['final_balance']
        log.info('found %s wallet with balance %s (%s)', chain, bal, wallet)
        return data.json()
    log.error('%s: failed to retrieve data about %s - likely a false match', chain, wallet)
    return None

def main(sitesource):
    log.debug('searching for cryptocurrency wallets')
    findings = {key: [] for key in rex.keys()}
    for currency, pattern in rex.items():
        for match in re.finditer(pattern, sitesource):
            log.debug('found a potential %s wallet: %s', currency, match.group())
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
    if len(findings['btc']) == 0:
        log.debug('no btc wallets found')
    if len(findings['eth']) == 0:
        log.debug('no eth wallets found')
    if len(findings['xmr']) == 0:
        log.debug('no xmr wallets found')
    return findings

def walletexplorer_inspect_and_pivot(address):
    walletid = ""
    addresses = []
    pageaddr = requests.get(f"https://www.walletexplorer.com/address/{address}", timeout=10)
    if pageaddr.text.find(f"Address {address} not found") > -1:
        log.warning('address %s not found, likely a false match', address)
        return walletid, addresses
    soup = BeautifulSoup(pageaddr.text, 'html.parser')
    linkwallet = soup.find("div", {"class": "walletnote"}).find('a').get('href')
    walletid =  linkwallet.split("/")
    if(len(walletid)>0):
        urlwalletaddress = f"https://www.walletexplorer.com/wallet/{walletid[2]}/addresses"
        walletaddr = requests.get(urlwalletaddress, timeout=10)
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
    return walletid, addresses

#getwallet_data('1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX', 'btc')
#getwallet_data('0x00000000219ab540356cbb839cbe05303d7705fa', 'eth')
#walletexplorer_inspect_and_pivot('bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6')
