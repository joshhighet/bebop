import logging
import requests

log = logging.getLogger(__name__)

def main(checkurl):
    with requests.get(checkurl, stream=True) as response:
        try:
            certificate_info = response.raw.connection.sock.getpeercert()
        except AttributeError:
            log.error('failed to retrieve certificate information')
            return None
        subject = dict(x[0] for x in certificate_info['subject'])
        issuer = dict(x[0] for x in certificate_info['issuer'])
        subjectAltName = [x[1] for x in certificate_info['subjectAltName']]
        certificate_info['subjectAltName'] = subjectAltName
        certificate_info['subject'] = subject
        certificate_info['issuer'] = issuer
        log.info('certificate found (serial: %s), signed by %s for %s', certificate_info['serialNumber'], issuer['commonName'], subject['commonName'])
        return certificate_info
