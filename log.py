import logging.config
import os
import pathlib
import yaml

logging.addLevelName(logging.INFO, 'I')
logging.addLevelName(logging.WARNING, 'W')
logging.addLevelName(logging.WARN, 'W')
logging.addLevelName(logging.ERROR, 'E')
logging.addLevelName(logging.DEBUG, 'D')
logging.addLevelName(logging.CRITICAL, 'C')


current_dir = pathlib.Path(__file__).parent
logging_config = os.environ.get('LOGGING_CONF', 'logging.yml')

with open(current_dir / logging_config, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)

log = logging.getLogger("nginxlogloader")
