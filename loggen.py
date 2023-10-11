from datetime import datetime, timedelta
import string
import random
import socket
import struct
import uuid


HOSTS = [
    "example.com",
    "nestfromthebest.com",
    "az.org",
]
USERAGENTS = [l.strip() for l in open("user-agents.txt")]
# USERAGENTS =[
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.47 Mobile/15E148 Safari/604.1",   
# ]


class LonEntryGen:
    LOG_FMT = 'I:{dt} [{pid}] req-id={req_id} req-time={req_time} status={status} resp-size={resp_size} req-method={method} req-path="{uri}" addr={addr} ua={ua} ref={ref} host={host} uct={uct} uht={uht} urt={urt} '
    TIME_FMT = '%Y-%m-%dT%H:%M:%S+00:00'
    REFERERS = ("https://www.google.com", "https://www.yandex.ru", "http://bing.com")
    RESP_CODES = (102, 200, 301, 302, 304, 400, 401, 403, 404, 500, 502, 504)
    METHODS =('GET', 'POST', 'HEAD')

    def __init__(self, logs=None, rate=None, start=None, gz=False):
        self.logs = logs or 600
        self.rate = rate or 10
        self.start = start or datetime.now()
        self.log_num = 0
        self.pid = random.randint(1, 2**8-1)
    
    def __str__(self) -> str:
        return f"LogEntryGen-{self.start.strftime('%Y-%m-%d')}"

    def __repr__(self) -> str:
        return self.__str__()

    def gen_req_id(self) -> str:
        return uuid.uuid4()
    
    def gen_resp_size(self) -> int:
        return random.randint(1234, 1048576)

    def gen_exec_time(self, lo, hi) -> float:
        return random.randrange(lo, hi)/1000.

    def gen_ua(self) -> str:
        return random.choice(USERAGENTS)

    def gen_host(self) -> str:
        return random.choice(HOSTS)

    def gen_method(self) -> str:
        return random.choice(self.METHODS)

    def gen_addr(self) -> str:
        return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

    def gen_uri(self) -> str:        
        sections = [
            "/about/",
            "/contacts/",
            f"/search?query={''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 64)))}",
            f"/item/id{random.randint(1, 2**10)}",
            f"/category/id{random.randint(1, 2**4)}"
        ]
        return random.choice(sections)

    def gen_ref(self):
        return random.choice(self.REFERERS)

    def gen_status(self) -> int:
        return random.choice(self.RESP_CODES)

    def gen(self, log_time) -> str:
        return self.LOG_FMT.format(
            dt=log_time,
            pid=self.pid,
            req_id=self.gen_req_id(),
            host=self.gen_host(),
            status=self.gen_status(),
            resp_size=self.gen_resp_size(),
            req_time=self.gen_exec_time(1, 20000),
            method=self.gen_method(),
            uri=self.gen_uri(),
            addr=self.gen_addr(),
            ua=self.gen_ua(),
            urt=self.gen_exec_time(1, 20000),
            uht=self.gen_exec_time(1, 20000),
            uct=self.gen_exec_time(1, 20000),
            ref=self.gen_ref(),
        )

    def __iter__(self):
        return self
    
    def __next__(self):
        if  self.logs <= self.log_num:         
            raise StopIteration
        seconds = self.log_num // self.rate
        dt = self.start + timedelta(seconds=seconds)
        self.log_num += 1
        return self.gen(dt.strftime(self.TIME_FMT))
    

if __name__ == '__main__':
    import time
    start = time.time()
    leg = LonEntryGen(logs=500_000, rate=100)
    for log in leg:
        # print(log)
        continue
    print(f"exec-time={time.time()-start}")