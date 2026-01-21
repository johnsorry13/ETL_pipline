import time
import colorlog
import yaml
from utils.proxy_manager import ProxyManager
from parsers.universal_parser import UniversalParser
from pathlib import Path
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

proxy_manager = ProxyManager()
full_config_path = (Path(__file__).parent
               / "configs" / "parser_store_config.yaml")

with open(full_config_path) as f:
    full_config = yaml.safe_load(f)

ozon_cfg = full_config['ozon']
ozon = UniversalParser(ozon_cfg, proxy_manager)


start_time = time.time()
ozon.run()
end_time = time.time()
logger.info(f"Время выполнения скрипта {round((end_time - start_time), 2)}")
