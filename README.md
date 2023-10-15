# Simple Nginx Access Log Processor. 

## Brief context
This is the generic example how to process logs in comfortable and fun ways.

## How to run
Run docker-compose project. It includes ClickHouse and Grafana. ClickHouse would be accessable by http://localhost:8123 and http://localhost:9000, Grafana would be accessable at http://localhost:3000
```bash
docker-compose up -d
```

Setup the virtual env
```bash
python3 -m virtualenv .venv
source .venv/bin/activate
python3 -m pip install -r requiremnet.txt
```

Change config.py by adding source of logs to the HOSTS var
```python
HOSTS = (
    ('example.com', 22, 'user', '<password>'),
)
```

Process logs
```bash
python3 main.py
```
