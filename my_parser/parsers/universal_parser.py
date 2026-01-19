import os
from datetime import date
import pandas as pd
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
        # proxies = {'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'}

        proxies = {
            'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
            'https': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'
        }

        return requests.get(url, proxies=proxies, timeout=10), proxy

    def parse(self, html, proxy):
        page = BeautifulSoup(html.text, 'html.parser')
        name = page.select_one(self._store_config['name']).text
        price = page.select_one(self._store_config['price']).text
        timestamp = date.today()
        item = {'название': name, 'цена': price, 'date': timestamp, 'proxy': proxy}
        return item

    def _parse_and_fetch(self, url):
        html, proxy = self.fetch(url)
        return self.parse(html, proxy)

    def streaming_result(self):
        urls_path = self._store_config['urls_path']
        all_urls = pd.read_excel(urls_path)
        urls = all_urls[all_urls['shop'] == self._store_config['shop']]['URLs'].tolist()
        with ThreadPoolExecutor (max_workers=self._store_config['max_workers']) as executor:
            results = {executor.submit(self._parse_and_fetch, url): url for url in urls}
            for future in as_completed(results):
                url = results[future]
                try:
                    result = future.result()
                    yield result
                except Exception as exc:
                    error_msg = f"{type(exc).__name__}: {str(exc)[:200]}"
                    yield {"ошибка": error_msg, "url": url}

    def run(self):
        filename = f'{self._store_config["shop"]}.csv'
        file_exists = os.path.isfile(filename)

        try:
            with open(f'{self._store_config["shop"]}.csv', 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                if not file_exists:
                    writer.writerow(['Название', 'Цена', 'Дата', 'Прокси'])
                for res in self.streaming_result():
                    if "ошибка" in res:
                        writer.writerow([f"Ошибка:{res['ошибка']}", f"URL: {res['url']}"])

                    else:
                        writer.writerow([res['название'], res['цена'], res['date']])
        except (OSError, IOError) as e:
            print (f'Ошибка записи файла {e}')

    def collect(self):
        pass








