#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://cryptography.io/en/latest/x509/reference/
import idna
import socks
import socket
import logging
from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID

import app.subprocessors as subprocessors
from .utilities import getproxyvalue

sockshost = getproxyvalue()[0]
socksport = getproxyvalue()[1]

log = logging.getLogger(__name__)

def commonserial(serial):
    with open('common/ssl-serials.txt', 'r', encoding='utf-8') as f:
        serials = {int(line.rstrip()) for line in f}
    if serial in serials:
        return True
    return False

def get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None

def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None

def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        return names
    except x509.ExtensionNotFound:
        return None

def get_subject(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None

def main(fqdn, port, usetor=True, doshodan=True, docensys=True, dozoome=True, dofofa=True):
    if port is None:
        logging.debug('port not specified, defaulting to 443')
        port = 443
    hostname_idna = idna.encode(fqdn)
    if usetor:
        log.debug('using tor proxy - %s:%s', sockshost, socksport)
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, sockshost, socksport)
        sock = socks.socksocket()
    else:
        sock = socket.socket()
    try:
        log.debug('connecting to %s:%s', fqdn, port)
        sock.settimeout(10)
        sock.connect((fqdn, port))
    except Exception as e:
        logging.error('connection error: %s', e)
        return None
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE
    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    try:
        sock_ssl.do_handshake()
    except SSL.Error as e:
        logging.error('ssl handshake error: %s', e)
    cert = sock_ssl.get_peer_certificate()
    if cert is None:
        logging.error('no certificate returned')
        return None
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()
    if commonserial(crypto_cert.serial_number) is False:
        if doshodan is True:
            subprocessors.query_shodan('ssl.cert.serial:"' + str(crypto_cert.serial_number) + '"')
        if docensys is True:
            querystr = 'services.tls.certificates.leaf_data.subject.serial_number:"' + str(crypto_cert.serial_number) + '"'
            subprocessors.query_censys(querystr)
        if dozoome is True:
            subprocessors.query_zoomeye('ssl.cert.serial:"' + str(crypto_cert.serial_number) + '"')
        if dofofa is True:
            subprocessors.query_fofa('cert=' + str(crypto_cert.serial_number))
    else:
        logging.debug('serial number match in common list, not searching shodan')
    data = {
        'alt_names': get_alt_names(crypto_cert),
        'common_name': get_common_name(crypto_cert),
        'subject': get_subject(crypto_cert),
        'issuer': get_issuer(crypto_cert),
        'serial': crypto_cert.serial_number,
        'not_before': crypto_cert.not_valid_before,
        'not_after': crypto_cert.not_valid_after
    }
    logging.debug(data)
    return data
