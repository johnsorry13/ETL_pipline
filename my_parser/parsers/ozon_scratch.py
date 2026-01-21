from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    # Убираем флаг автоматизации через JS (обязательно!)
    page.add_init_script("delete navigator.__proto__.webdriver")

    page.goto("https://www.ozon.ru/product/kryshka-voronka-gorloviny-bachka-omyvatelya-omyvayki-vag-art-6v0955485-819727356/")
    page.wait_for_timeout(5000)  # ждём 5 секунд (для демонстрации)
    browser.close()