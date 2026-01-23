import os
import re
import ast
import logging
import time
from datetime import date
import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from .base_parser import BaseParser
from queue import Queue
from playwright.sync_api import sync_playwright
import threading
from itertools import cycle
from pathlib import Path



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


class UniversalParser(BaseParser):
    logger = logging.getLogger(__name__)
    _local = threading.local()
    def __init__(self, store_config, proxy=1):
        self._store_config = store_config
        if proxy == 1:
            self._proxy_manager = ProxyManager()
        else:
            self._proxy_manager = None
        self._urls = self.load_urls()

    def _get_browser(self):
        """Возвращает браузер, привязанный к текущему потоку."""
        if not hasattr(UniversalParser._local, 'playwright'):
            UniversalParser._local.playwright = sync_playwright().start()
            UniversalParser._local.browser = UniversalParser._local.playwright.chromium.launch(
                headless=self._store_config.get('headless', False)
            )
        return UniversalParser._local.browser


    def load_urls(self):
        self.logger.info("Загружаю список URL для парсинга")
        try:
            urls_path = self._store_config['urls_path']
            all_urls = pd.read_excel(urls_path)
            urls = all_urls[all_urls['shop'] == self._store_config['shop']]['URLs'].tolist()
            self.logger.info(f"Успешно загружено {len(urls)} ссылок")
            return urls
        except Exception as e:
            self.logger.error(f"Ошибка загрузки списка URL {e}", exc_info=True)
            raise

    def fetch_browser(self, url: str):

        if self._proxy_manager:
            proxy = self._proxy_manager.get_proxy()
            proxy_dict = {
                    "server": f"{proxy['host']}:{proxy['port']}",
                    "username": f"{proxy['login']}",
                    "password": f"{proxy['password']}"
                }
        else:
            proxy = None
            proxy_dict = None
        browser = self._get_browser()
        context = browser.new_context(
            proxy=proxy_dict,
            viewport={"width": 1920, "height": 1080}
        )
        print()
        try:
            page = context.new_page()
            page.add_init_script("delete navigator.__proto__.webdriver")
            page.goto(url)
            page.wait_for_selector("h1.tsHeadline550Medium", timeout=10000)
            html = page.content()
            return html, proxy
        finally:
            context.close()


    def fetch_https(self, url: str):
        if self._proxy_manager:
            self.logger.debug(f"Загружаю прокси для {url}")
            try:
                proxy = self._proxy_manager.get_proxy()
                self.logger.debug(f"Прокси {proxy['host']} успешно загружен для {url}")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки прокси для {url}", exc_info=True)
                raise
            # proxies = {'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'}

            proxies = {
                'http': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
                'https': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'
            }
            self.logger.debug(f"Загрузка страницы: {url}, прокси: {proxy['host']}")
        else:
            proxies = None
            proxy = None
        try:
            html = requests.get(url, proxies=proxies, timeout=10).text
            # html.raise_for_status()

            self.logger.debug(f"Страница: {url} успешно загружена, прокси: {proxy['host'] if proxy else 'None'}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки: {url}, прокси: {proxy['host'] if proxy else 'None'}")
            raise
        return html, proxy

    def fetch(self, url):
        if self._store_config['source'] == 'browser':
            self.logger.info('Начинаю загрузку через браузер')
            return self.fetch_browser(url)
        if self._store_config['source'] == 'https':
            self.logger.info('Начинаю загрузку через https')
            return self.fetch_https(url)

    #Безопасное извлечение из JS или СSS селектора
    def _safe_extract_text(self, page, html, field_config, default="N/A"):
        if field_config is None:
            return default
        if 'js_var' in field_config:
            try:
                e_var_name = re.escape(field_config['js_var'])
                pattern = e_var_name + '\s*=\s*(\{[^}]+\});'
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    js_obj = ast.literal_eval(match.group(1))
                    print(js_obj)
                    return str(js_obj.get(field_config['js_name'], default))

            except Exception as e:
                self.logger.debug(f"JS-парсинг не удался для {field_config['js_var']}: {e}")

        if 'css' in field_config:
            elem = page.select_one(field_config['css'])
            return elem.get_text(strip=True) if elem else default
        self.logger.info(f"Парсинг не удался для Css {field_config['css']}")
        return default

    def parse(self, html, proxy, url):
        page = BeautifulSoup(html, 'html.parser')

        timestamp = date.today()
        item = {'name': self._safe_extract_text(page, html, self._store_config['fields'].get('name')),
                'reg_price': self._safe_extract_text(page, html, self._store_config['fields'].get('reg_price')),
                'price': self._safe_extract_text(page, html, self._store_config['fields'].get('price')),
                'brand': self._safe_extract_text(page, html, self._store_config['fields'].get('brand')),
                'sku': self._safe_extract_text(page, html, self._store_config['fields'].get('sku')),
                'date': timestamp,
                'proxy': proxy['host'] if proxy else 'без прокси',
                'url': url}

        return item

    def _parse_and_fetch(self, url):
        html, proxy = self.fetch(url)
        return self.parse(html, proxy, url)

    def streaming_result(self):
        with ThreadPoolExecutor (max_workers=self._store_config['max_workers']) as executor:
            results = {executor.submit(self._parse_and_fetch, url): url for url in self._urls[:1]}
            completed_count = 0
            for future in as_completed(results):
                url = results[future]
                completed_count += 1
                try:
                    result = future.result()
                    self.logger.info(f"URL {completed_count} из {len(self._urls)}: "
                                     f"{result['url']}: прокси: {result['proxy']}")
                    yield result
                except Exception as e:
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    yield {"error": error_msg, "url": url}

    def run(self):
        filename = f'{self._store_config["shop"]}.csv'
        file_exists = os.path.isfile(filename)

        try:
            with open(f'{self._store_config["shop"]}.csv', 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                if not file_exists:
                    writer.writerow(['Название', 'Рег_цена', 'Цена', 'Бренд',
                                     'sku', 'Дата', 'Прокси', 'Ошибка', 'URL'])
                for res in self.streaming_result():
                    if "error" in res:
                        writer.writerow(["",
                                         "",
                                         "",
                                         "",
                                         "",
                                         "",
                                         "",
                                         res.get('error', ''),
                                         res.get('url', '')])

                    else:
                        writer.writerow([res.get('name', ""),
                                         res.get('reg_price'),
                                         res.get('price', ""),
                                         res.get('brand', ""),
                                         res.get('sku', ""),
                                         res.get('date', ""),
                                         res.get('proxy', ""),
                                         res.get('error', ""),
                                         res.get('url', "")])
        except (OSError, IOError) as e:
            print (f'Ошибка записи файла {e}')

    def collect(self):
        pass








