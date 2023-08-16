#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import logging
import asyncio
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector

log = logging.getLogger(__name__)

import title
from utilities import getsocks, useragentstr

async def is_catch_all(session, location, attempts=3):
    for _ in range(attempts):
        random_path = "/" + str(uuid.uuid4())
        uri = location + random_path
        try:
            log.debug('scanning %s as for catch-all validation', uri)
            async with session.get(uri, timeout=10) as response:
                if response.status != 200:  
                    return False
        except Exception as e:
            log.error('error fetching %s - %s', uri, e)
            return False
    return True

interesting_paths = [
    {'uri': '/server-status', 'code': 200, 'text': 'Apache'},
    {'uri': '/install/index.php', 'code': 200, 'text': 'Installation Wizard'},
    {'uri': '/server-info', 'code': 200, 'text': 'Apache'},
    {'uri': '/wp-login.php', 'code': 200, 'text': 'login'},
    {'uri': '/xmlrpc.php', 'code': 405, 'text': 'XML-RPC server accepts POST requests only'},
    {'uri': '/phpinfo.php', 'code': 200, 'text': 'This program makes use of the Zend'},
    {'uri': '/cpanel', 'code': 200, 'text': 'cPanel, Inc'},
    {'uri': '/phpmyadmin/', 'code': 200, 'text': 'Welcome to phpMyAdmin'},
    {'uri': '/phpsysinfo/', 'code': 200, 'text': 'phpSysInfo'},
    {'uri': '/adminer/', 'code': 200, 'text': 'Adminer'},
    {'uri': '/joomla', 'code': 200, 'text': 'Joomla'},
    {'uri': '/drupal', 'code': 200, 'text': 'Drupal'},
    {'uri': '/jenkins', 'code': 200, 'text': 'Jenkins'},
    {'uri': '/grafana', 'code': 200, 'text': 'Grafana'},
    {'uri': '/kibana', 'code': 200, 'text': 'Kibana'},
    {'uri': '/.well-known/security.txt', 'code': 200, 'text': 'Contact'},
    {'uri': '/manager/html', 'code': 200, 'text': 'Apache Tomcat'},
    {'uri': '/robots.txt', 'code': 200, 'text': None},
    {'uri': '/sitemap.xml', 'code': 200, 'text': None},
    {'uri': '/admin', 'code': 200, 'text': None},
    {'uri': '/administrator', 'code': 200, 'text': None},
    {'uri': '/wp-admin', 'code': 200, 'text': None},
    {'uri': '/wp-admin/admin-ajax.php', 'code': 200, 'text': None},
    {'uri': '/.git', 'code': 200, 'text': None},
    {'uri': '/.env', 'code': 200, 'text': None},
    {'uri': '/WEB-INF/web.xml', 'code': 200, 'text': None},
    {'uri': '/config.php', 'code': 200, 'text': None},
    {'uri': '/backup.sql', 'code': 200, 'text': None},
    {'uri': '/backup.tar.gz', 'code': 200, 'text': None},
    {'uri': '/wp-config.php.bak', 'code': 200, 'text': None},
    {'uri': '/install.php', 'code': 200, 'text': None},
    {'uri': '/readme.html', 'code': 200, 'text': None},
    {'uri': '/CHANGELOG.txt', 'code': 200, 'text': None},
    {'uri': '/LICENSE.txt', 'code': 200, 'text': None},
    {'uri': '/api/v1/users', 'code': 200, 'text': None},
    {'uri': '/api/v1/tokens', 'code': 200, 'text': None},
    {'uri': '/api-docs', 'code': 200, 'text': None},
    {'uri': '/test.php', 'code': 200, 'text': None},
    {'uri': '/debug.php', 'code': 200, 'text': None},
    {'uri': '/info.php', 'code': 200, 'text': None},
    {'uri': '/uploads', 'code': 200, 'text': None},
    {'uri': '/files', 'code': 200, 'text': None},
    {'uri': '/media', 'code': 200, 'text': None},
    {'uri': '/500.html', 'code': 200, 'text': None},
    {'uri': '/.htaccess', 'code': 200, 'text': None},
    {'uri': '/.htpasswd', 'code': 200, 'text': None},
    {'uri': '/.svn', 'code': 200, 'text': None},
    {'uri': '/.git/config', 'code': 200, 'text': None},
    {'uri': '/README.md', 'code': 200, 'text': None},
    {'uri': '/.DS_Store', 'code': 200, 'text': None},
    {'uri': '/swagger-ui.html', 'code': 200, 'text': None},
    {'uri': '/console', 'code': 200, 'text': None},
    {'uri': '/.dockerenv', 'code': 200, 'text': None},
    {'uri': '/.gitlab-ci.yml', 'code': 200, 'text': None},
    {'uri': '/.travis.yml', 'code': 200, 'text': None},
    {'uri': '/.circleci/config.yml', 'code': 200, 'text': None},
    {'uri': '/error_log', 'code': 200, 'text': None},
    {'uri': '/access_log', 'code': 200, 'text': None},
    {'uri': '/modx', 'code': 200, 'text': 'MODX'},
    {'uri': '/typo3', 'code': 200, 'text': 'TYPO3'},
    {'uri': '/symfony', 'code': 200, 'text': 'Symfony'},
    {'uri': '/swagger', 'code': 200, 'text': 'Swagger'},
    {'uri': '/redmine', 'code': 200, 'text': 'Redmine'},
    {'uri': '/gitweb', 'code': 200, 'text': 'GitWeb'},
    {'uri': '/git', 'code': 200, 'text': 'GitLab'},
    {'uri': '/composer.lock', 'code': 200, 'text': None},
    {'uri': '/package-lock.json', 'code': 200, 'text': None},
    {'uri': '/yarn.lock', 'code': 200, 'text': None},
    {'uri': '/.TemporaryItems', 'code': 200, 'text': None},
    {'uri': '/.access.php', 'code': 200, 'text': None},
    {'uri': '/.buildpath', 'code': 200, 'text': None},
    {'uri': '/.env.example', 'code': 200, 'text': None},
    {'uri': '/.ftpquota', 'code': 200, 'text': None},
    {'uri': '/.gitattributes', 'code': 200, 'text': None},
    {'uri': '/.github', 'code': 200, 'text': None},
    {'uri': '/.gitignore', 'code': 200, 'text': None},
    {'uri': '/.hg', 'code': 200, 'text': None},
    {'uri': '/.hgignore', 'code': 200, 'text': None},
    {'uri': '/.htaccess', 'code': 200, 'text': None},
    {'uri': '/.htpasswd', 'code': 200, 'text': None},
    {'uri': '/.htpasswds', 'code': 200, 'text': None},
    {'uri': '/.idea', 'code': 200, 'text': None},
    {'uri': '/.localized', 'code': 200, 'text': None},
    {'uri': '/.platform', 'code': 200, 'text': None},
    {'uri': '/.project', 'code': 200, 'text': None},
    {'uri': '/.qidb', 'code': 200, 'text': None},
    {'uri': '/.quarantine', 'code': 200, 'text': None},
    {'uri': '/.sass-cache', 'code': 200, 'text': None},
    {'uri': '/.section.php', 'code': 200, 'text': None},
    {'uri': '/.settings', 'code': 200, 'text': None},
    {'uri': '/.smileys', 'code': 200, 'text': None},
    {'uri': '/.styleci.yml', 'code': 200, 'text': None},
    {'uri': '/.tmb', 'code': 200, 'text': None},
    {'uri': '/.top.menu.php', 'code': 200, 'text': None},
    {'uri': '/.user.ini', 'code': 200, 'text': None},
    {'uri': '/.vscode', 'code': 200, 'text': None},
    {'uri': '/.well-known', 'code': 200, 'text': None},
    {'uri': '/.ini', 'code': 200, 'text': None}
]

async def fetch(location, path, session):
    uri = location + path['uri']
    log.debug('scanning %s - expecting %s', uri, path['code'])
    try:
        async with session.get(uri) as response:
            text = await response.text()
            if response.status == path['code']:
                if path['text'] is None:
                    log.info(f'found {path["code"]} at {uri}')
                elif path['text'] in text:
                    log.info(f'found {path["code"]} at {uri}')
                else:
                    log.debug(f'found {path["code"]} at {uri} but no match for {path["text"]}')
            else:
                log.debug(f'found {response.status} at {uri}')
    except Exception as e:
        log.error('error fetching %s - %s', uri, e)
        logging.debug(e)

async def main(location, usetor=True, max_concurrent_requests=5):
    if location.endswith('/'):
        location = location[:-1]
    if usetor:
        reqproxies = getsocks(aio_fmt=True)
    else:
        reqproxies = None
    logging.debug('requesting: %s - usetor:%s', location, usetor)
    logging.debug('using proxies: %s', reqproxies)
    timeout = ClientTimeout(total=30)
    sem = asyncio.Semaphore(max_concurrent_requests)
    connector = ProxyConnector.from_url(reqproxies.get('https')) if reqproxies else None
    async with ClientSession(headers={'User-Agent': useragentstr}, timeout=timeout, trust_env=True, connector=connector) as session:
        catch_all_detected = await is_catch_all(session, location)
        if catch_all_detected:
            log.warning("catch-all response-code behavior detected - path-based checks will be skipped")
            return
        tasks = []
        for path in interesting_paths:
            async with sem:
                tasks.append(fetch(location, path, session))
        await asyncio.gather(*tasks)
