#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import logging

log = logging.getLogger(__name__)

if os.getenv('ZOOMEYE_API_KEY', None) != None:
    zoomeye_authkey = os.getenv('ZOOMEYE_API_KEY')
    zoomeye_data = requests.get('https://api.zoomeye.org/resources-info', headers={'API-KEY': zoomeye_authkey})
    print('############# ZoomEye')
    print(str(zoomeye_data.json()['quota_info']['remain_total_quota']) + ' remaining credits')
else:
    log.error('ZOOMEYE_API_KEY missing')

if os.getenv('BINARYEDGE_API_KEY', None) != None:
    binaryedge_authkey = os.getenv('BINARYEDGE_API_KEY')
    binaryedge_data = requests.get('https://api.binaryedge.io/v2/user/subscription', headers={'X-Key': binaryedge_authkey})
    requests_used = binaryedge_data.json()['requests_left']  # Actually contains used count
    requests_plan = binaryedge_data.json()['requests_plan']
    remaining_requests = requests_plan - requests_used
    print('############## BinaryEdge')
    print(f"used {requests_used} out of {requests_plan} available credits - {remaining_requests} remaining")
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
    shodan_data = requests.get('https://api.shodan.io/api-info?key={}'.format(shodan_authkey))
    query_credits = shodan_data.json()['query_credits']
    print('############## Shodan')
    print(f"{query_credits} query credits remaining for current month")
else:
    log.error('SHODAN_API_KEY missing')

if os.getenv('CENSYS_API_ID', None) and os.getenv('CENSYS_API_SECRET', None) != None:
    censys_authid = os.getenv('CENSYS_API_ID')
    censys_authsecret = os.getenv('CENSYS_API_SECRET')
    censys_data = requests.get('https://search.censys.io/api/v1/account', auth=(censys_authid, censys_authsecret))
    quota_info = censys_data.json()['quota']
    used_queries = quota_info['used']
    allowed_queries = quota_info['allowance']
    remaining_queries = allowed_queries - used_queries
    print('############## Censys')
    print(f"used {used_queries} of {allowed_queries} available queries for current month - {remaining_queries} remaining")
else:
    log.error('CENSYS_API_ID missing')

if os.getenv('SECURITYTRAILS_API_KEY', None) != None:
    st_authkey = os.getenv('SECURITYTRAILS_API_KEY')
    st_headers = {'APIKEY': st_authkey}
    st_data = requests.get(
        'https://api.securitytrails.com/v1/account/usage', headers=st_headers)
    st_usage = st_data.json()
    allowed_usage = st_usage.get('allowed_monthly_usage')
    current_usage = st_usage.get('current_monthly_usage')
    print('############## SecurityTrails')
    print(f"used {current_usage} of {allowed_usage} avail credits for current month")
else:
    log.error('SECURITYTRAILS_API_KEY missing')

if os.getenv('URLSCAN_API_KEY', None) != None:
    us_authkey = os.getenv('URLSCAN_API_KEY')
    us_headers = {'API-Key': us_authkey}
    us_data = requests.get('https://urlscan.io/user/quotas/', headers=us_headers)
    us_quotas = us_data.json().get('limits', {}).get('search', {})
    print('############## urlscan.io')
    minute_quota = us_quotas.get('minute', {})
    print(f"used {minute_quota.get('used')} out of {minute_quota.get('limit')} avail credits for current minute")
    hourly_quota = us_quotas.get('hour', {})
    print(f"used {hourly_quota.get('used')} out of {hourly_quota.get('limit')} avail credits for current hour")
    daily_quota = us_quotas.get('day', {})
    print(f"used {daily_quota.get('used')} out of {daily_quota.get('limit')} avail credits for today")
else:
    log.error('URLSCAN_API_KEY missing')
    
if os.getenv('VIRUSTOTAL_API_KEY', None) != None:
    vt_authkey = os.getenv('VIRUSTOTAL_API_KEY')
    vt_headers = {'x-apikey': vt_authkey}
    vt_data = requests.get('https://www.virustotal.com/api/v3/users/' + vt_authkey, headers=vt_headers)
    vt_quotas = vt_data.json().get('data', {}).get('attributes', {}).get('quotas', {})
    print('############## VirusTotal')
    daily_quota = vt_quotas.get('api_requests_daily', {})
    print(f"used {daily_quota.get('used')} out of {daily_quota.get('allowed')} avail credits for today")
    hourly_quota = vt_quotas.get('api_requests_hourly', {})
    print(f"used {hourly_quota.get('used')} out of {hourly_quota.get('allowed')} avail credits for current hour")
    monthly_quota = vt_quotas.get('api_requests_monthly', {})
    print(f"used {monthly_quota.get('used')} out of {monthly_quota.get('allowed')} avail credits for current month")    
else:
    log.error('VIRUSTOTAL_API_KEY missing')
