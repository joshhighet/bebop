#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
builds nmap response
'''
import json
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def commandgen(fqdn, usetor=True, max_scanport=10, useragent='Mozilla'):
    basecmd='\
nmap -sT -PN -n -sV --open -oX - --top-ports %s \
--version-intensity 4 --script ssh-hostkey,ssh-auth-methods,banner \
--script-args http.useragent="%s",ssh_hostkey=sha256,md5 %s | xq' % (max_scanport, useragent, fqdn)
    if usetor:
        basecmd = 'proxychains4 -f proxychains.conf ' + basecmd
    return basecmd

def portdata(port):
    logging.debug('found port: %s', str(port['@portid']))
    portinf = {
        'port': port['@portid'],
        'name': None,
        'product': None,
        'service': None,
        'ostype': None,
        'cpe': None,
        'banner': None,
        'hostprints': [],
        'shellauthmethods': []
    }
    if '@name' in port['service']:
        portinf['name'] = port['service']['@name']
    if '@product' in port['service']:
        portinf['product'] = port['service']['@product']
    if '@conf' in port['service']:
        portinf['confidence'] = port['service']['@conf']
    if '@version' in port['service']:
        portinf['version'] = port['service']['@version']
    if '@ostype' in port['service']:
        portinf['ostype'] = port['service']['@ostype']
    if 'cpe' in port['service']:
        portinf['cpe'] = port['service']['cpe']
    if 'script' in port:
        for script in port['script']:
            try:
                if script['@id'] == 'banner':
                    portinf['banner'] = script['@output']
                elif script['@id'] == 'ssh-hostkey':
                    for line in script['@output'].splitlines():
                        if line and not line.isspace():
                            portinf['hostprints'].append(line.strip())
                elif script['@id'] == 'ssh-auth-methods':
                    if 'publickey' in script['@output']:
                        portinf['shellauthmethods'].append('publickey')
                    if 'password' in script['@output']:
                        portinf['shellauthmethods'].append('password')
                    if 'keyboard-interactive' in script['@output']:
                        portinf['shellauthmethods'].append('keyboard-interactive')
            except TypeError as te:
                logging.debug('failed to parse banner script')
                logging.debug(te)
                logging.debug(script)
    return portinf

def main(fqdn):
    scanobj = {
        'args': None,
        'ports': None,
        'time': None
    }
    command = commandgen(fqdn)
    output = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    out_json = output.stdout
    logging.debug(out_json)
    scanout = json.loads(out_json)
    scanobj['args'] = scanout['nmaprun']['@args']
    if 'host' not in scanout['nmaprun']:
        logging.debug('no open ports')
        return
    portarr = scanout['nmaprun']['host']['ports']['port']
    logging.debug(scanout['nmaprun']['@args'])
    if scanout['nmaprun']['host']['status']['@state'] == 'up':
        scanobj['ports'] = []
        if isinstance(portarr, list):
            for port in portarr:
                scanobj['ports'].append(portdata(port))
                logging.info('found port: %s', str(port['@portid']))
        else:
            scanobj['ports'].append(portdata(portarr))
    else:
        logging.debug('no open ports discovered')
    scanobj['time'] = int(float(scanout['nmaprun']['runstats']['finished']['@elapsed']))
    logging.debug(scanout)
    return scanobj
