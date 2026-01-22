import os
import re
import ast
import logging
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

class BrowserManager:
    def __init__(self, size=3, headless=True):
        self.size = size
        self._headless = headless
        self._initialized = False
        self._queue = Queue()
        self._sync_playwright = sync_playwright().start()
        for _ in range(self.size):
            browser = self._sync_playwright.chromium.launch(headless=self._headless)
            self._queue.put(browser)

    def get_browser(self):
        return self._queue.get()
    def return_browser(self, browser):
        return self._queue.put(browser)
    def close_all_browsers(self):
        while not self._queue.empty():
            browser = self._queue.get()
            browser.close()
        self._sync_playwright.stop()

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

proxy_manager = ProxyManager()
browser_manager = BrowserManager()
class UniversalParser(BaseParser):
    logger = logging.getLogger(__name__)
    def __init__(self, store_config, proxy_manager, browser_manager):
        self._store_config = store_config
        self._proxy_manager = proxy_manager
        self._urls = self.load_urls()
        if self._store_config['source'] == 'browser':
            self._browser_manager = browser_manager


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


    def feth_browser(self, url: str):
        browser = self._browser_manager.get_browser()
        proxy = self._proxy_manager.get_proxy()
        context = browser.new_context(
            proxy={
                "server": f"http://proxy-{proxy['host']}:{proxy['port']}:",
                "username": f"{proxy['login']}",
                "password": f"{proxy['password']}"
            },
            user_agent="Mozilla/5.0 (Custom Bot)",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()
        page.add_init_script("delete navigator.__proto__.webdriver")

        page.goto(url)
        
        html = page.content()
        return html

        pass

    def fetch_https(self, url: str):
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
        try:
            html = requests.get(url, proxies=proxies, timeout=10)
            html.raise_for_status()
            self.logger.debug(f"Страница: {url} успешно загружена, прокси: {proxy['host']}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки: {url}, прокси: {proxy['host']}")
            raise
        return html, proxy

    def fetch(self, url):
        if self._store_config['source'] == 'browser':
            return self.feth_browser(url)
        if self._store_config['sourse'] == 'https':
            return self.fetch_https(url)

    #Безопасное извлечение из JS или СSS селектора
    def _safe_extract_text(self, page, html, field_config, default="N/A"):
        html_text = html.text
        if 'js_var' in field_config:
            try:
                e_var_name = re.escape(field_config['js_var'])
                pattern = r"var " + e_var_name + '\s*=\s*(\{[^}]+\});'
                match = re.search(pattern, html_text, re.DOTALL)
                if match:
                    js_obj = ast.literal_eval(match.group(1))
                    return str(js_obj.get(field_config['js_name'], default))

            except Exception as e:
                self.logger.debug(f"JS-парсинг не удался для {field_config['js_var']}: {e}")

        if 'css' in field_config:
            elem = page.select_one(field_config['css'])
            return elem.get_text(strip=True) if elem else default
        return default

    def parse(self, html, proxy, url):
        page = BeautifulSoup(html.text, 'html.parser')

        timestamp = date.today()
        item = {'name': self._safe_extract_text(page, html, self._store_config['fields']['name']),
                'reg_price': self._safe_extract_text(page, html, self._store_config['fields']['reg_price']),
                'price': self._safe_extract_text(page, html, self._store_config['fields']['price']),
                'brand': self._safe_extract_text(page, html, self._store_config['fields']['brand']),
                'sku': self._safe_extract_text(page, html, self._store_config['fields']['sku']),
                'date': timestamp,
                'proxy': proxy['host'],
                'url': url}

        return item

    def _parse_and_fetch(self, url):
        html, proxy = self.fetch(url)
        return self.parse(html, proxy, url)

    def streaming_result(self):
        with ThreadPoolExecutor (max_workers=self._store_config['max_workers']) as executor:
            results = {executor.submit(self._parse_and_fetch, url): url for url in self._urls[:50]}
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
                    error_msg = f"{type(e).__name__}: {str(e)[:16]}"
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








