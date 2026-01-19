import time
import yaml

from parsers.proxy_manager import ProxyManager
from parsers.universal_parser import UniversalParser
from pathlib import Path

proxy_manager = ProxyManager()
full_config_path = (Path(__file__).parent
               / "configs" / "parser_store_config.yaml")

with open(full_config_path) as f:
    full_config = yaml.safe_load(f)

maxidom_cfg = full_config['maxidom']

maxidom = UniversalParser(maxidom_cfg, proxy_manager)

maxidom.run()

