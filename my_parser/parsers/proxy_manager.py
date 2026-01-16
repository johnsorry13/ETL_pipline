import yaml
from pathlib import Path
from itertools import cycle
import threading

class ProxyManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = (Path(__file__).parent.parent
                                / "configs" / "proxies_example.yaml")

        with open (config_path) as f:
            self.config = yaml.safe_load(f)['proxies']

        self._proxy_cycle = cycle(self.config)
        self._lock = threading.Lock()

    def get_proxy(self):
        with self._lock:
            return next(self._proxy_cycle)



