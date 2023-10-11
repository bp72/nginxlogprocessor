import time
from datetime import datetime, timedelta
import random
import os

import clickhouse_connect

from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, DOWNLOAD_TO, HOSTS, CHUNK_SIZE, USE_SYNTETIC, HOW_MANY_SYNTETIC
from fetcher import SSHFetcher
from loader import createDatabases, createTables, loadToClickHouse
from log import log
from logparser import readFile
from loggen import LonEntryGen


def processFeed(feed, client, chunk_size=10_000):
    total = 0
    start = time.time()
    for chunk in readFile(feed, chunk_size=chunk_size):    
        chunk_start_time = time.time()
        total += len(chunk)
        loadToClickHouse(client, chunk=chunk)
        log.info(f'process {feed=} inserted={len(chunk)} {total=} exec-time={time.time()-chunk_start_time}')
    log.info(f'{feed=} status=done exec-time={time.time()-start}')
    

def main():
    client = clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT)

    # create databases and tables if those do not exist
    # in order to have tables empty, pass drop_table=True and
    # tables would be recreated.
    createDatabases(client=client)
    createTables(client=client, drop_table=False)

    # this function checks if file does not exist in registry of processed files
    # and returns True. 
    # This basically was created to handle the situation if some file was not processed in time
    def shouldProcessFeed(host, filename):
        query = f"""SELECT filename FROM logs.logfiles WHERE filename='{filename}@{host}'"""
        result = client.query(query)
        return result.row_count == 0

    def markAsProcessed(host, filename):
        client.insert('logs.logfiles', [(f"{filename}@{host}",)], column_names=['filename',])
    
    if not USE_SYNTETIC:
        for hostCreds in HOSTS:
            fetcher = SSHFetcher(*hostCreds)
            for filepath in fetcher.fetchLogs("/var/log/nginx", "*access*.log-*", DOWNLOAD_TO, shouldProcessFeed):
                processFeed(feed=filepath, client=client, chunk_size=CHUNK_SIZE)
                markAsProcessed(host=hostCreds[0], filename=os.path.basename(filepath))
        return
   
    # !!!Attention!!!
    # Generator LonEntryGen turned out to be slow. I'm not sure about the reasons at the moment.
    # However most of the time is cosumed by __generation__ code, not the ClickHouse insertions
    for file_no in range(HOW_MANY_SYNTETIC):
        fname = f"generated-log-{file_no}"
        host = "loggen"
        if shouldProcessFeed(host, fname):
            feed = LonEntryGen(
                logs=random.randint(50_000, 200_000),
                rate=random.randint(10, 20),
                start=datetime.now()-timedelta(hours=file_no)
            )
            processFeed(feed=feed, client=client, chunk_size=CHUNK_SIZE)
            markAsProcessed(host=host, filename=fname)


if __name__ == "__main__":
    main()
