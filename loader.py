from log import log

def createDatabases(client):
    client.command('''CREATE DATABASE IF NOT EXISTS nginx''')
    client.command('''CREATE DATABASE IF NOT EXISTS logs''')


def createTables(client, drop_table=False):
    if drop_table:
        client.command('''DROP TABLE IF EXISTS nginx.access''')
        client.command('''DROP TABLE IF EXISTS logs.logfiles''')
    client.command('''
        CREATE TABLE IF NOT EXISTS nginx.access (
        reqid String,
        ts DateTime64(3),               
        level Enum(''=0, 'debug'=1, 'info'=2, 'warn'=3 ,'error'=4),
        domain String,
        uri String,
        ua String,                          
        ref String,
        is_bot Boolean,
        is_mobile Boolean,
        is_tablet Boolean,
        is_pc Boolean,
        client String,
        duration Float32,
        response_code UInt16,
        addrIPv4 Nullable(IPv4),
        addrIPv6 Nullable(IPv6),
        upstream_connect_time Float32,
        upstream_header_time Float32,
        upstream_response_time Float32
        )
        ENGINE MergeTree
        PRIMARY KEY reqid
        ORDER BY reqid
    ''')

    client.command('''
CREATE TABLE IF NOT EXISTS logs.logfiles (
    filename String
)
ENGINE MergeTree
PRIMARY KEY filename
ORDER BY filename
''')


def loadToClickHouse(client, chunk):
    cols = [
        'reqid',
        'ts',
        'level',
        'domain',
        'uri',
        'ua', 
        'ref',
        'is_bot',
        'is_mobile',
        'is_tablet',
        'is_pc',
        'client',
        'duration',
        'response_code',
        'addrIPv4',
        'addrIPv6',
        'upstream_connect_time',
        'upstream_header_time',
        'upstream_response_time',
    ]
    client.insert('nginx.access', chunk, column_names=cols)

