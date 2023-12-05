#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
builds nmap response
'''
import os
import json
import logging
import subprocess

from .utilities import gen_chainconfig

log = logging.getLogger(__name__)

def portdata(port):
    log.info('found port: %s', str(port['@portid']))
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
            except TypeError:
                log.debug('failed to parse banner script: %f', TypeError)
                log.debug(script)
    return portinf

def main(fqdn, useragent, usetor=True, max_scanport=10):
    command='\
nmap -sT -PN -n -sV --open -oX - --top-ports %s \
--version-intensity 4 --script ssh-hostkey,ssh-auth-methods,banner \
--script-args http.useragent="%s",ssh_hostkey=sha256,md5 %s | xq' % (max_scanport, useragent, fqdn)
    if usetor:
        gen_chainconfig()
        command = 'proxychains4 -f ../proxychains.conf ' + command
    log.info('commencing portscan on %s', fqdn)
    log.debug('command: %s', command)
    output = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    scanout = json.loads(output.stdout)
    scanout['args'] = scanout['nmaprun']['@args']
    if 'host' not in scanout['nmaprun']:
        log.info('no open ports discovered?')
        return scanout
    portarr = scanout['nmaprun']['host']['ports']['port']
    log.debug(scanout['nmaprun']['@args'])
    if scanout['nmaprun']['host']['status']['@state'] == 'up':
        scanout['ports'] = []
        if isinstance(portarr, list):
            for port in portarr:
                pdata = portdata(port)
                log.info(pdata)
                scanout['ports'].append(pdata)
        else:
            pdata = portdata(portarr)
            log.info(pdata)
            scanout['ports'].append(pdata)
    else:
        log.info('no open ports discovered?')
        log.error(scanout)
    scanout['time'] = int(float(scanout['nmaprun']['runstats']['finished']['@elapsed']))
    log.debug(scanout)
    return scanout
