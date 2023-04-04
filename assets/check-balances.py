import os
import json
import requests
import logging

keys = {
    'ZOOMEYE_API_KEY': os.getenv('ZOOMEYE_API_KEY', None),
    'BINARYEDGE_API_KEY':os.getenv('BINARYEDGE_API_KEY', None),
    'CENSYS_API_ID': os.getenv('CENSYS_API_ID', None),
    'CENSYS_API_SECRET': os.getenv('CENSYS_API_SECRET', None),
    'SHODAN_API_KEY': os.getenv('SHODAN_API_KEY', None),
    'FOFA_API_KEY': os.getenv('FOFA_API_KEY', None),
    'FOFA_API_MAIL': os.getenv('FOFA_API_MAIL', None)
}

for key, value in keys.items():
    if value is None:
        logging.error('missing key(s)!')
        os._exit(1)

def fofacheck():
    fofa_authkey = os.getenv('FOFA_API_KEY')
    fofa_authmail = os.getenv('FOFA_API_MAIL')
    fofa_data = requests.get(
        'https://fofa.info/api/v1/info/my?email={}&key={}'.format(fofa_authmail, fofa_authkey))
    return fofa_data.json()

def shodancheck():
    shodan_authkey = os.getenv('SHODAN_API_KEY')
    shodan_data = requests.get(
        'https://api.shodan.io/api-info?key={}'.format(shodan_authkey))
    return shodan_data.json()

def binaryedgecheck():
    binaryedge_authkey = os.getenv('BINARYEDGE_API_KEY')
    binaryedge_data = requests.get(
        'https://api.binaryedge.io/v2/user/subscription', headers={'X-Key': binaryedge_authkey})
    return binaryedge_data.json()

def cenyscheck():
    censys_authid = os.getenv('CENSYS_API_ID')
    censys_authsecret = os.getenv('CENSYS_API_SECRET')
    censys_data = requests.get(
        'https://search.censys.io/api/v1/account', auth=(censys_authid, censys_authsecret))
    return censys_data.json()

def zoomeyecheck():
    zoomeye_authkey = os.getenv('ZOOMEYE_API_KEY')
    zoomeye_data = requests.get('https://api.zoomeye.org/resources-info', headers={'API-KEY': zoomeye_authkey})
    return zoomeye_data.json()
    
if __name__ == '__main__':
    print('balance check')
    print('---------------------')
    print('################ fofa')
    fofa_data = fofacheck()
    print('coins: {}'.format(fofa_data['fcoin']))
    print('points: {}'.format(fofa_data['fofa_point']))
    print('remaining queries: {}'.format(fofa_data['remain_api_query']))
    print('remaining data: {}'.format(fofa_data['remain_api_data']))
    print('---------------------')
    print('############## shodan')
    sho_data = shodancheck()
    print('scan credits: {}'.format(sho_data['scan_credits']))
    print('query credits: {}'.format(sho_data['query_credits']))
    print('---------------------')
    print('########## binaryedge')
    bin_data = binaryedgecheck()
    print('credits: {}'.format(bin_data['requests_left']))
    print('---------------------')
    print('############## censys')
    queries_left = cenyscheck()['quota']['allowance'] - cenyscheck()['quota']['used']
    print('remaining queries: {}'.format(queries_left))
    print('---------------------')
    print('############# zoomeye')
    print('remaining queries: {}'.format(zoomeyecheck()['quota_info']['remain_total_quota']))
    print('---------------------')