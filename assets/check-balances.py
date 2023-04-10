import os
import json
import requests
import logging

log = logging.getLogger(__name__)

if os.getenv('ZOOMEYE_API_KEY', None) != None:
    zoomeye_authkey = os.getenv('ZOOMEYE_API_KEY')
    zoomeye_data = requests.get('https://api.zoomeye.org/resources-info', headers={'API-KEY': zoomeye_authkey})
    print('############# zoomeye')
    print('remaining queries: {}'.format(zoomeye_data.json()['quota_info']['remain_total_quota']))
else:
    log.error('ZOOMEYE_API_KEY missing')

if os.getenv('BINARYEDGE_API_KEY', None) != None:
    binaryedge_authkey = os.getenv('BINARYEDGE_API_KEY')
    binaryedge_data = requests.get(
        'https://api.binaryedge.io/v2/user/subscription', headers={'X-Key': binaryedge_authkey})
    print('########## binaryedge')
    print('credits: {}'.format(binaryedge_data.json()['requests_left']))
else:
    log.error('BINARYEDGE_API_KEY missing')

if os.getenv('FOFA_API_KEY', None) != None:
    fofa_authkey = os.getenv('FOFA_API_KEY')
    fofa_authmail = os.getenv('FOFA_API_MAIL')
    fofa_data = requests.get(
        'https://fofa.info/api/v1/info/my?email={}&key={}'.format(fofa_authmail, fofa_authkey))
    print('################ fofa')
    print('coins: {}'.format(fofa_data.json()['fcoin']))
    print('points: {}'.format(fofa_data.json()['fofa_point']))
    print('remaining queries: {}'.format(fofa_data.json()['remain_api_query']))
    print('remaining data: {}'.format(fofa_data.json()['remain_api_data']))
else:
    log.error('FOFA_API_KEY missing')

if os.getenv('SHODAN_API_KEY', None) != None:
    shodan_authkey = os.getenv('SHODAN_API_KEY')
    shodan_data = requests.get(
        'https://api.shodan.io/api-info?key={}'.format(shodan_authkey))
    print('############## shodan')
    print('scan credits: {}'.format(shodan_data.json()['scan_credits']))
    print('query credits: {}'.format(shodan_data.json()['query_credits']))
else:
    log.error('SHODAN_API_KEY missing')

if os.getenv('CENSYS_API_ID', None) != None:
    censys_authid = os.getenv('CENSYS_API_ID')
    censys_authsecret = os.getenv('CENSYS_API_SECRET')
    censys_data = requests.get(
        'https://search.censys.io/api/v1/account', auth=(censys_authid, censys_authsecret))
    print('############## censys')
    queries_left = censys_data.json()['quota']['allowance'] - censys_data.json()['quota']['used']
    print('remaining queries: {}'.format(queries_left))
else:
    log.error('CENSYS_API_ID missing')
