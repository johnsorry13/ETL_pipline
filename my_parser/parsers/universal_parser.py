import requests
from bs4 import BeautifulSoup

def fetch_page(url: str):
    return requests.get(url).text

def parse_html(html: str, cfg: dict):
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.select_one(cfg['name']).text
    price = soup.select_one(cfg['price']).text
    return name, price


