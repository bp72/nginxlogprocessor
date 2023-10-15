import datetime
import gzip
import ipaddress
import user_agents

from loggen import LonEntryGen


# log_format  main  'I:$time_iso8601 [$pid] req-id=$request_id req-time=$request_time '
#                   'status=$status resp-size=$body_bytes_sent '
#                   'req-method=$request_method req-path="$request_uri" '
#                   'addr=$remote_addr addr=$http_cf_connecting_ip addr=$http_x_forwarded_for '
#                   'ua=$http_user_agent '
#                   'ref=$http_referer '
#                   'host=$http_host '
#                   'uct=$upstream_connect_time uht=$upstream_header_time urt=$upstream_response_time ';


keys = (
    'req-id=',
    'req-time=',
    'status=',
    'resp-size=',
    'req-method=',
    'req-path=',
    'addr=',
    'ua=',
    'ref=',
    'host=',
    'uct=', # upstream_connect_time
    'uht=', # upstream_header_time
    'urt=', # upstream_response_time
    'eol=', # dummy
)

def parseKeyVal(s: str):
    res = {}
    for i in range(0, len(keys)-1):
        key = keys[i]
        next_key = keys[i+1]
        
        pos =  s.find(key)
        next_key_pos = s.find(next_key)-1 if next_key != "eol" else len(s)

        if pos == -1:
            continue

        val = s[pos+len(key):next_key_pos]
        res[key[:-1]] = val.strip('"')
    
    res['addr'] = res['addr'].split(' ')[0]

    return res

def levelConv(s):
    if s == "I":
        return "info"
    if s == "D":
        return "debug"
    if s == "W":
        return "warn"
    if s == "E":
        return "error"
    return ""    

def getIPv4(addr):
    a = ipaddress.ip_address(address=addr)
    if isinstance(a, ipaddress.IPv4Address):
        return addr

def getIPv6(addr):
    a = ipaddress.ip_address(address=addr)
    if isinstance(a, ipaddress.IPv6Address):
        return addr

def smartfloat(s):
    try:
        return float(s)
    except:
        return 0.0

def readGzip(filepath):
    with gzip.open(filepath, 'rb') as h:
        for line in h:
            yield line.decode()

def readPlainText(filepath):
    with open(filepath) as h:
        for line in h:
            yield line

def read(feed):
    if isinstance(feed, (str,)):
        return readGzip(filepath=feed) if feed.endswith("gz") else readPlainText(filepath=feed)
    if isinstance(feed, LonEntryGen):
        return feed
    return None


def readFile(filepath, chunk_size=10_000):
    rows = []

    for line in read(filepath):            
        line = line.strip()
        level = levelConv(line[0])
        dt = datetime.datetime.strptime(line[2:27], '%Y-%m-%dT%H:%M:%S%z')
        pid = line[29:line.find(']')]
        line = line[line.find(']')+2:]
        kv = parseKeyVal(line)
        ua = user_agents.parse(kv['ua'])

        rows.append((
            kv['req-id'],
            dt,
            level,
            kv['host'],
            kv['req-path'],
            kv['ua'],
            kv['ref'],
            ua.is_bot,
            ua.is_mobile,
            ua.is_tablet,
            ua.is_pc,
            ua.browser.family,
            kv['req-time'],
            int(kv['status']),
            getIPv4(kv['addr']),
            getIPv6(kv['addr']),
            smartfloat(kv['uct']),
            smartfloat(kv['uht']),
            smartfloat(kv['urt']),
            )
        )
        if len(rows) == chunk_size:
            yield rows
            rows = []
    
    yield rows
