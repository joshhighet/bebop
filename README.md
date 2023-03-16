# bebop

---

inspired by the now defunct [onionscan](https://github.com/s-rah/onionscan), bebop is my spin on a suite checks if you're attempting to reveal and uncloak hidden services

bebop it is aimed to help expedite some of the many mundane tasks involved in investigating onion services and locations fronted by cdn's

```mermaid
graph LR
    subgraph subprocessors
        subgraph cryptocurrency[coin data]
        blockcypher
        walletexplorer
        blockcypher -..-> |pivot|walletexplorer
        walletexplorer -..-> blockcypher
        end
        subgraph netscans[scan data]
        shodan
        censys
        binaryedge
        zoomeye
        end
    end
    lookupsaver[(if rare value)]
    fuzzlist[(fuzzlist)]
    opndir[check for open directories]
    cryptoc[check for wallets]
    checks([/server-status\n/robots.txt\netc])
    anchor([input url]) -->mainget>get site content]
    mainget --> fuzz[directory/file enumeration]
    fuzz -..-> fuzzlist
    fuzzlist -..-> fuzz
    anchor --> scan(port/service scan)
    anchor --> checker(config checks)
    checker -..-> checks
    mainget --> favicon[get favicon fuzzyhash]
    mainget --> sslserial[get ssl serial]
    sslserial --> lookupsaver
    favicon --> lookupsaver
    mainget --> title[fetch page title]
    title --> lookupsaver
    mainget --> headers[inspect headers]
    headers --> |if etag|netscans
    lookupsaver --> netscans
    mainget --> spider[spider recursive pages]
    mainget --> opndir
    spider --> opndir
    mainget --> cryptoc
    spider --> cryptoc
    cryptoc -..-> ifsupportedcoin[/if LTC/XMR/BTC/]
    ifsupportedcoin --> cryptocurrency
```

# methods

- favicon detection
- etag detection
- response header analysis (return rare/interesting headers)
- technology identification (port scanning & service identification)
- spidering (return samesite, subdomain and external URLs)
- open directory checks
- webpage title extraction
- email extraction
- wallet extraction & balance fetching (xmr,btc,eth)
- certificate trailing (serial lookup)

# technicals

## prerequisites

you will need to make a Tor routable SOCKS5 proxy available to this image

leverage any existing infrastructure, create your own or follow one of the below methods

1. create a simple single-relay proxy with [joshhighet/torsocc](https://github.com/joshhighet/torsocc/pkgs/container/torsocc)

    ```shell
    docker run -p9050:9050 ghcr.io/joshhighet/torsocc:latest
    ```

2. making a large number of requests? - consider leveraging [joshhighet/multisocks](https://github.com/joshhighet/multisocks), an haproxy balanced relay framework

    ```shell
    git clone https://github.com/joshhighet/multisocks
    docker compose --file multisocks/docker-compose.yml up --detach
    ```
    
by default, the proxy location is set to `host.docker.internal:9050` - this can be overwrote through environment variables, refer to the `building` section for more

### page spider

[pagespider.py](app/pagespider.py) simply parses the given source code and returens two objects;

- URL's contained within the source on the same FQDN
- URL's contained within the source on an alternate domain or subdomain

### config checks

[configcheck.py](app/configcheck.py) is an extensible set of page-based checks. the list `interesting_paths` defines various checks

each check should consist of three elements, and will look similar to the below 

```python
{'uri': '/server-status', 'code': 200, 'text': 'Apache'},
```

if the response object is unknown or there is uncertainty with string-matches, use `None` as the value for `text`

  - the URI
  - the expected response status code
  - a string expected within the page source

### favicon

[favicon.py](app/favicon.py) will attempt to find a favicon on the webpage

- the favicon discovery will attempt to parse the icon from any HTML, falling back to hardcoded paths
- if found, the favicon is downloaded and an [MurmurHash](https://commons.apache.org/proper/commons-codec/apidocs/org/apache/commons/codec/digest/MurmurHash3.html) is computed
- the hash is searched against the following engines where credentials are provided
`shodan:http.favicon.hash`, `censys:services.http.response.favicons.md5_hash`, `binaryedge:web.favicon.mmh3` & `zoomeye:iconhash`

_to avoid noise, a list of the top 200 favicons have been added to this repository - if a finding is matched, it will not be considered unique - see the housekeeping section for details_

### headers

[headers.py](app/headers.py) does some light analysis on response headers. there are four key outputs

- `etag` - is a server etag is found, it is searched against <todo>
- `server` - the value for the `Server` HTTP header
- `cookies` - any cookies dropped by the server during the request
- `interesting_headers` - any rare/interesting headers. essentially the response headers with exclusions - see [headers.txt](app/common/headers.txt)

### port scanning

[portscan.py](app/portscan.py) leverages nmap, [proxychains-ng](https://github.com/rofl0r/proxychains-ng) and [yq](https://github.com/kislyuk/yq)

- yq is used to turn the XML outputted by nmap into JSON
- unless specified only the top ten ports are scanned
- the full command ran can be seen here on [explainshell](https://explainshell.com/explain?cmd=nmap+-sT+-PN+-n+-sV+--version-intensity+3+--script+ssh-hostkey%2Cbanner%2Chttp-title+--script-args+http.useragent%3D%22USERAGENT%22%2Cssh_hostkey%3Dall+--top-ports+200)

a number of nse scripts are used - these include
- [ssh-hostkey](https://nmap.org/nsedoc/scripts/ssh-hostkey.html)
- [banner](https://nmap.org/nsedoc/scripts/banner.html)
- [http-title](https://nmap.org/nsedoc/scripts/http-title.html)
- [ssh-auth-methods](https://nmap.org/nsedoc/scripts/ssh-auth-methods.html)

### open directories

[opendir.py](app/opendir.py) is a simple check that attempts to ascertain wether the current pgae is an open directory

the current implementation simply looks for the string `Index of` within a given pages source.

this is used in conjunction with the spider. i.e get all urls, check for directories

### title

[title.py](app/title.py) simply parses the site title out of a page. the text you see on a tab ? that thing

# building

_at build time you can inject a custom proxy location with `SOCKS_HOST` & `SOCKS_PORT`_

```shell
git clone https://github.com/joshhighet/bebop
docker build --build-arg SOCKS_HOST=10.20.30.40 --build-arg SOCKS_PORT=8080 bebop/app -t bebop
```

# running

## external services

if given credentials, binaryedge, censys, shodan & zoomeye can be used to for enrichment, see the above diagram for specific use criteria

_using one, any or all external data repositories is optional and only done when authorisation parameters are explicitly provided_

- to leverage Censys, provide both your `CENSYS_API_ID` and the accompanying `CENSYS_API_SECRET`.
> you can fetch this from [search.censys.io/account/api](https://search.censys.io/account/api)

- to leverage Shodan, provide your `SHODAN_API_KEY`.
> you can fetch this from [account.shodan.io](https://account.shodan.io)

- to leverage Binaryedge, provide your `BINARYEDGE_API_KEY`
> you can fetch this from [app.binaryedge.io/account/api](https://app.binaryedge.io/account/api)

- to leverage ZoomEye, provide your `ZOOMEYE_API_KEY`
> you can fetch this from [zoomeye.org/profile](https://www.zoomeye.org/profile)

if you have already built the image locally, run

```shell
docker run bebop facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion
```

run from ghcr with the below

unless specified (like below) the SOCKS5 proxy will default to `host.docker.internal:9050`

```shell
docker run \
-e SOCKS_HOST=yourproxy.fqdn \
-e SOCKS_PORT=9050 \
-e SHODAN_API_KEY=yourkey \
-e CENSYS_API_ID=yourid \
-e CENSYS_API_SECRET=yourkey \
-e BINARYEDGE_API_KEY=yourkey \
-e ZOOMEYE_API_KEY=yourkey \
ghcr.io/joshhighet/bebop:latest http://ciadotgov4sjwlzihbbgxnqg3xiyrg7so2r2o3lt5wz5ypk4sxyjstad.onion
```

# housekeeping

to avoid consuming unneccesary credits polling subprocessors a list of common results for a few tasks are stored as text files within this repo.

this includes a list of the top 1000 favicon fuzzyhashes, top 1500 ssl serials and the top 1000 server titles - if a match is found against these, it's unlikely to be a useful enough data-point to bother polling the likes of <todo> for

these files should be updated every now and then. to do so, run the following

```shell
# for favicons
shodan stats --facets http.favicon.hash:1000 port:80,443 \
| grep -oE '^[-]?[0-9]+' \
> common/favicon-hashes.txt
echo 0 >> common/favicon-hashes.txt
# for http titles
shodan stats --facets http.title:1000 port:80,443 \
| grep -oE '^[^0-9]+' \
| sed -r 's/^[[:space:]]+//;s/[[:space:]]+$//' \
| sed '/^[[:space:]]*$/d' \
> common/http-titles.txt
echo '404 Error Page' >> common/http-titles.txt
# for x509 serials
shodan stats --facets ssl.cert.serial:2000 port:443,8443 \
| grep -o '^[^ ]*' \
| sed '/Top/d' \
> common/ssl-serials.txt
```
