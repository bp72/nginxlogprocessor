HOSTS = (
    # Format, it is gonna be used as positional args, 
    # so the order is important.
    # In case there is not user and/or pass just skip it.
    # ('<your-ip-or-host>', 22, '<user>', '<password>'),
)

DOWNLOAD_TO = '/tmp'

CLICKHOUSE_HOST = '127.0.0.1'
CLICKHOUSE_PORT = 8123

CHUNK_SIZE = 50_000
USE_SYNTETIC = True
HOW_MANY_SYNTETIC = 100