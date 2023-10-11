import os
import paramiko
from scp import SCPClient
from log import log


class SSHFetcher:
    def __init__(self, host, port=22, user=None, password=None) -> None:
        self.host = host
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, port, user, password)
        log.info(f'connect {host=} {port=} {user=} {password=}')
    
    def fetchLogs(self, src, mask, dst, should_process_fn):
        cmd = f"ls {src}/{mask}"
        log.info(f"run {cmd=}")
        _, ssh_stdout, _ = self.client.exec_command(f"ls {src}/{mask}")

        if ssh_stdout.readable():       
            resp = ssh_stdout.read()

            for filepath in resp.splitlines():
                _src = filepath.decode()
                filename = os.path.basename(_src)
                
                if not should_process_fn(self.host, filename):
                    log.warn(f'already processed {filename=} host={self.host}')
                    continue
                
                _src = filepath.decode()
                _dst = f"{dst}/{os.path.basename(_src)}"
                log.info(f"download src={_src} dst={_dst}")                
                self.fetchLog(filepath.decode(), _dst)
                yield _dst


    def fetchLog(self, src, dst):
        scp = SCPClient(self.client.get_transport())
        scp.get(remote_path=src, local_path=dst)        


if __name__ == '__main__':
    import random
    from config import HOSTS, DOWNLOAD_TO
    
    creds = HOSTS[0]

    def f(*args, **kwargs):
        return random.choice([True, False])

    ftr = SSHFetcher(*creds)   
    for fp in ftr.fetchLogs("/var/log/nginx", "*.log-*", DOWNLOAD_TO, f):
        log.info(fp)


