import configparser
from dataclasses import dataclass


@dataclass
class ConnectionData:
    config = configparser.ConfigParser()
    config.read('./config.ini')
    backend_server_address = config['CONNECTION']['backend_server']