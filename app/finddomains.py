import socket
import socks
import logging
import subprocessors
import dns.resolver
import dns.name
import dns.rdatatype
from utilities import getproxyvalue

log = logging.getLogger(__name__)

def get_proxy_socket():
    proxyaddr, proxyport = getproxyvalue()
    socks.set_default_proxy(socks.SOCKS5, proxyaddr, proxyport)
    socket.socket = socks.socksocket
    return socks.socksocket()

def reverse_dns_lookup(ip_address):
    try:
        reverse_name = dns.reversename.from_address(ip_address)
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(reverse_name, 'PTR')
        return str(answers[0])[:-1]
    except dns.resolver.NoAnswer:
        logging.debug(f"no rDNS record for {ip_address}")
        return None
    except Exception as e:
        logging.error(f"error in rDNS lookup for {ip_address}: {e}")
        return None

def check_hostname_resolvematch(hostnames, target_ip):
    resolved_hostnames = []
    resolver = dns.resolver.Resolver()
    for hostname in hostnames:
        try:
            answers = resolver.resolve(hostname, 'A')
            for rdata in answers:
                if str(rdata) == target_ip:
                    resolved_hostnames.append(hostname)
                    break
        except dns.resolver.NXDOMAIN:
            logging.debug(f"no resolution for {hostname}")
        except Exception as e:
            logging.debug(f"failed to resolve {hostname}: {e}")
    return resolved_hostnames

def main(ip):
    log.info('starting finddomains')
    reverse_dns_hostname = reverse_dns_lookup(ip)
    log.info('querying virustotal for resolutions')
    vtires = subprocessors.query_resolutions_virustotal(ip)
    log.info('querying urlscan for resolutions')
    urlsres = subprocessors.query_resolutions_urlscan(ip)
    log.info('querying securitytrails for resolutions')
    strailres = subprocessors.query_resolutions_securitytrails(ip)
    combined_hostnames = vtires.union(urlsres, strailres)
    if reverse_dns_hostname:
        combined_hostnames.add(reverse_dns_hostname)
    log.debug(f"total hostnames: {combined_hostnames}")
    log.info(f'found {len(combined_hostnames)} unique hostnames, checking resolution')
    resolved_hostnames = check_hostname_resolvematch(combined_hostnames, ip)
    log.info(f"found {len(resolved_hostnames)} hostnames resolving to {ip}")
    log.debug(f"resolved hostnames: {resolved_hostnames}")
