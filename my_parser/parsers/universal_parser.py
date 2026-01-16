import requests
from bs4 import BeautifulSoup

from .base_parser import BaseParser

class UniversalParser(BaseParser):
    def __init__(self, store_config, proxy_manager):
        self._store_config = store_config
        self._proxy_manager = proxy_manager
    def fetch(self, url: str):
        proxy = self._proxy_manager.get_proxy()
        proxies = {'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'}
        return requests.get(url, proxies=proxies)

    def parse(self, html):
        page = BeautifulSoup(html.text, 'html.parser')
        name = page.select_one(self._store_config['name']).text
        price = page.select_one(self._store_config['price']).text
        item = {'название': name, 'цена': price}
        return item


    def collect(self):
        pass








