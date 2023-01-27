#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import socket
import logging
import tldextract
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

socksaddr = os.environ.get('SOCKS_HOST', '127.0.0.1')
socksport = os.environ.get('SOCKS_PORT', 9050)

file_checks = ['proxychains.conf', 'common/headers.txt']
path_checks = ['proxychains4','nmap']

def checktcp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((str(host), int(port)))
    sock.close()
    if result == 0:
        return True
    return False

def getfqdn(url):
    url_object = tldextract.extract(url)
    if url_object.subdomain:
        return url_object.subdomain + '.' + url_object.domain + '.' + url_object.suffix
    return url_object.domain + '.' + url_object.suffix

def getbaseurl(url):
    urlparse_object = urlparse(url)
    if urlparse_object.path == '':
        return url
    return urlparse_object.scheme + '://' + urlparse_object.netloc
    
def getsocks():
    if not checktcp(socksaddr, socksport):
        logging.critical('failed socks5 preflight socket check (' + socksaddr + ':' + str(socksport) + ' unreachable)')
        sys.exit(1)
    oproxies = {
        'http':  'socks5h://' + socksaddr + ':' + str(socksport),
        'https': 'socks5h://' + socksaddr + ':' + str(socksport)
    }
    return oproxies

def preflight():
    for path_item in path_checks:
        check = shutil.which(path_item)
        if check is None:
            print('{} not found'.format(path_item))
            sys.exit(1)
    for file in file_checks:
        if not os.path.isfile(file):
            print('{} not found'.format(file))
            sys.exit(1)
