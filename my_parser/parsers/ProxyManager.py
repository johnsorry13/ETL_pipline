import yaml
from pathlib import Path

current_file = Path(__file__)
config_path = current_file.parent.parent / "configs" / "proxies_example.yaml"

with open(config_path) as f:
    prx_config = yaml.safe_load(f)

class ProxyManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = (Path(__file__).current_file.parent.parent
                                / "configs" / "proxies_example.yaml")

        with open (config_path) as f:
            self.config = yaml.safe_load(f)

    def get_proxy(self):
        pass




