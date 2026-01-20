import os
import logging
from datetime import date
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from .base_parser import BaseParser


class UniversalParser(BaseParser):
    logger = logging.getLogger(__name__)
    def __init__(self, store_config, proxy_manager):
        self._store_config = store_config
        self._proxy_manager = proxy_manager
        self._urls = self.load_urls()

    def load_urls(self):
        self.logger.info("Загружаю список URL для парсинга")
        try:
            urls_path = self._store_config['urls_path']
            all_urls = pd.read_excel(urls_path)
            urls = all_urls[all_urls['shop'] == self._store_config['shop']]['URLs'].tolist()
            self.logger.info(f"Успешно загружено {len(urls)} ссылок")
            return urls
        except Exception as exec:
            self.logger.error(f"Ошибка загрузки списка URL {exec}", exc_info=True)
            raise


    def fetch(self, url: str):
        self.logger.debug(f"Загружаю прокси для {url}")
        try:
            proxy = self._proxy_manager.get_proxy()
            self.logger.debug(f"Прокси {proxy['host']} успешно загружен для {url}")
        except Exception as exec:
            self.logger.error(f"Ошибка загрузки прокси для {url}", exc_info=True)
            raise
        # proxies = {'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'}

        proxies = {
            'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
            'https': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'
        }
        self.logger.debug(f"Загрузка страницы: {url}, прокси: {proxy['host']}")
        try:
            html = requests.get(url, proxies=proxies, timeout=10)
            html.raise_for_status()
            self.logger.debug(f"Страница: {url} успешно загружена, прокси: {proxy['host']}")
        except Exception as exec:
            self.logger.error(f"Ошибка загрузки: {url}, прокси: {proxy['host']}")
            raise
        return html, proxy

    def parse(self, html, proxy, url):
        page = BeautifulSoup(html.text, 'html.parser')
        name = page.select_one(self._store_config['name']).text
        price = page.select_one(self._store_config['price']).text
        timestamp = date.today()
        item = {'name': name,
                'price': price,
                'date': timestamp,
                'proxy': proxy['host'],
                'url': url}

        return item

    def _parse_and_fetch(self, url):
        html, proxy = self.fetch(url)
        return self.parse(html, proxy, url)

    def streaming_result(self):
        with ThreadPoolExecutor (max_workers=self._store_config['max_workers']) as executor:
            results = {executor.submit(self._parse_and_fetch, url): url for url in self._urls[:10]}
            completed_count = 0
            for future in as_completed(results):
                url = results[future]
                completed_count += 1
                try:
                    result = future.result()
                    self.logger.info(f"URL {completed_count} из {len(self._urls)}: "
                                     f"{result['url']}: прокси: {result['proxy']}")
                    yield result
                except Exception as exc:
                    error_msg = f"{type(exc).__name__}: {str(exc)[:16]}"
                    yield {"error": error_msg, "url": url}

    def run(self):
        filename = f'{self._store_config["shop"]}.csv'
        file_exists = os.path.isfile(filename)

        try:
            with open(f'{self._store_config["shop"]}.csv', 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                if not file_exists:
                    writer.writerow(['Название', 'Цена', 'Дата', 'Прокси', 'Ошибка', 'URL'])
                for res in self.streaming_result():
                    if "error" in res:
                        writer.writerow(["",
                                         "",
                                         "",
                                         "",
                                         res.get('error', ''),
                                         res.get('url', '')])

                    else:
                        writer.writerow([res.get('name', ""),
                                         res.get('price', ""),
                                         res.get('date', ""),
                                         res.get('proxy', ""),
                                         res.get('error', ''),
                                         res.get('url', "")])
        except (OSError, IOError) as e:
            print (f'Ошибка записи файла {e}')

    def collect(self):
        pass








