import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
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

    def _parse_and_fetch(self, url):
        html = self.fetch(url)
        return self.parse(html)

    def streaming_result(self):
        urls = self._store_config['urls']
        with ThreadPoolExecutor (max_workers=self._store_config['max_workers']) as executor:
            results = {executor.submit(self._parse_and_fetch, url): url for url in urls}
            for future in as_completed(results):
                url = results[future]
                try:
                    print(future.result())
                    yield future.result()
                except Exception as exc:
                    yield {"ошибка": exc, "url": url}

    def run(self):

        with open(f'{self._store_config["shop"]}.csv', 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Название', 'Цена'])
            for res in self.streaming_result():
                writer.writerow([res['название'], res['цена']])


    def collect(self):
        pass








