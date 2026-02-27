import faker
import psycopg
import os
import pandas as pd
import logging
from typing import List, Tuple, Any
import random
import datetime

db_config = {'host': 'localhost',
             'dbname': 'oltp_test',
             'user': 'postgres',
             'password': '1'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OltpDataGenerator:
    def __init__(self, db_config: dict = None):
        self.faker = faker.Faker(locale='ru_RU')
        self.db_config = db_config or {
            "host": os.getenv("DB_HOST", "localhost"),
            "dbname": os.getenv("DB_NAME", "oltp_test"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "1")
        }
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg.connect(**self.db_config)
            logger.info("Подключение к БД прошло успешно")
        except Exception as e:
            logger.info(f"Ошибка подключения к БД", {e})

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Соединение с БД закрыто")
        else:
            logger.info("Соединение уже закрыто")

    def _execute_batch(self, query: str, generated_data):
        if not self.conn:
            raise ConnectionError("Невозможно выполнить запрос: соединение с БД отсутствует.")
        cur = self.conn.cursor()
        try:
            cur.execute_values(query, generated_data)
            self.conn.commit()
            logger.info(f"Вставлено {len(generated_data)} записей")
        except Exception as e:
            self.conn.rollback()
            logger.info("Ошибка вставки в БД")
        finally:
            cur.close()

    def generate_static_data(self, table: str, values: List[Tuple]):
        """
        Универсальный метод для заполнения небольших справочников.
        """
        if not values:
            return

        query = f"""
            INSERT INTO {table} VALUES %s
            ON CONFLICT DO NOTHING
        """
        self._execute_batch(query, values)

    def generate_store(self):
        generated_data = []
        for _ in range(15):
            store = {'name': f"ГИП{self.faker.random_int(min=1, max=100)}",
                        'city': self.faker.city(),
                        'street': self.faker.street_address(),
                        'phone': self.faker.phone_number(),
                        'is_active': self.faker.boolean()
            }
            record = (store['name'], store['city'], store['street'], store['phone'], store['is_active'])
            generated_data.append(record)
        query = """ INSERT INTO store (name, city, street, phone, is_active)
             VALUES %s"""
        self._execute_batch(query, generated_data)

    def generate_competitors(self):
        self.generate_static_data('competitor', [('ozon', ), ('maxidom', )])

    def generate_supplier(self):
        generated_data = []
        for _ in range(20):
            supplier = {'name': self.faker.company(),
                        'inn': str(self.faker.random_number(digits=10)),
                        'address': self.faker.address(),
                        'email': self.faker.email(),
                        'is_active': self.faker.boolean()
            }
            record = (supplier['name'], supplier['inn'], supplier['address'], supplier['email'], supplier['is_active'])
            generated_data.append(record)
        query = """ INSERT INTO supplier (name, inn, address, email, is_active)
             VALUES %s """
        self._execute_batch(query, generated_data)

    def generate_currency(self):
        self.generate_static_data('currency', [('RUB', ), ('USD', ), ('CNY',)])

    def generate_uom(self):
        self.generate_static_data('uom', [('шт', ), ('уп',), ('м',)])

    def generate_tax_rate(self):
        self.generate_static_data('tax_rate', [('НДС', 22, )])

    def generate_categories(self):
        df = pd.read_excel('product_matrix.xlsx')['УК'].unique().tolist()
        generated_data = [(elem, elem[1:3]) for elem in df]
        query = """INSERT INTO categories (name, level_id) VALUES %s"""
        self._execute_batch(query, generated_data)

    def generate_employees(self):
        generated_data = []
        for _ in range(5):
            employee = {'name': self.faker.name()
            }
            record = (employee['name'],)
            generated_data.append(record)
        query = """ INSERT INTO employees (name)
             VALUES %s """
        self._execute_batch(query, generated_data)

    def get_id_from_table(self, table: str):
        if not self.conn:
            return []
        cur = self.conn.cursor()
        try:
            query = f"""SELECT id FROM {table}"""
            cur.execute(query)
            results = [row[0] for row in cur.fetchall()]
            return results
        except Exception as e:
            return []
        finally:
            cur.close()

    def generate_products(self):
        df = pd.read_excel('product_matrix.xlsx')['Название'].unique().tolist()
        generated_data = []
        cat_id = self.get_id_from_table('categories')
        uom_id = self.get_id_from_table('uom')
        BRAND_POOL = [
            "VestaHome", "TechnoStar", "BioLife", "UrbanStyle", "GreenWave",
            "NordicLine", "SmartChoice", "EcoPure", "MetalPro", "SoftTouch",
            "Kvantum", "AuroraFit", "DomMaster", "FlexiGo", "PrimeZone",
            "VelvetCode", "IronClad", "FreshDay", "OptimaPlus", "SkyLink"
        ]

        for elem in df:
            product = {"name": elem,
                       "current_price": random.uniform(50.0, 10000.0),
                       "category_id": random.choice(cat_id),
                        "brand": random.choice(BRAND_POOL),
                        "uom_id": random.choice(uom_id),
                        "is_active": self.faker.boolean()
            }
            record = (product['name'], product['current_price'], product['category_id'], product['brand'],
                      product['uom_id'], product['is_active'])
            generated_data.append(record)
        query = """INSERT INTO product (name, current_price, category_id, brand, uom_id, is_active) 
        VALUES %s"""
        self._execute_batch(query, generated_data)

    def generate_warehouses(self):
        """
        Генерация складов по принципу: 1 магазин = 1 склад.
        Перед генерацией таблица очищается во избежание дубликатов.
        """
        if not self.conn:
            print("Ошибка: Нет соединения с базой данных.")
            return

        cur = self.conn.cursor()
        try:
            # 1. Очищаем таблицу перед новой генерацией (так как нет уникальных ограничений)
            print("Очистка таблицы warehouse...")
            cur.execute("TRUNCATE TABLE warehouse RESTART IDENTITY CASCADE")
            self.conn.commit()

            # 2. Получаем список всех магазинов (ID и название)
            cur.execute("SELECT id, name FROM store")
            stores = cur.fetchall()

            if not stores:
                print("Предупреждение: Таблица store пуста. Генерация складов пропущена.")
                return

            print(f"Генерация складов для {len(stores)} магазинов...")

            generated_data = []

            for store_id, store_name in stores:
                # Формируем имя склада на основе имени магазина
                warehouse_name = f"Склад {store_name}"
                phone = self.faker.phone_number()

                record = (
                    warehouse_name,
                    store_id,
                    phone
                )
                generated_data.append(record)

            # 3. Вставка данных
            query = """INSERT INTO warehouse (name, store_id, phone) VALUES %s"""

            self._execute_batch(query, generated_data)
            print(f"Успешно создано {len(generated_data)} складов.")

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при генерации складов: {e}")
        finally:
            cur.close()

    def generate_operation_type(self):
        self.generate_static_data('operation_type', [('Продажа',), ('Закупка',)])

    def generate_sale_status(self):
        """Заполнение справочника статусов продаж."""
        statuses = [('Новый',), ('Оплачен',), ('В доставке',), ('Завершен',), ('Отменен',)]

        cur = self.conn.cursor()
        try:
            # Очищаем таблицу перед вставкой, чтобы избежать дублей и сбросить ID
            cur.execute("TRUNCATE TABLE sale_status RESTART IDENTITY CASCADE")

            query = "INSERT INTO sale_status (status) VALUES (%s)"
            cur.executemany(query, statuses)
            self.conn.commit()
            print(f"Добавлено {len(statuses)} статусов продаж.")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при генерации статусов продаж: {e}")
        finally:
            cur.close()

    def generate_purchase_status(self):
        """Заполнение справочника статусов закупок."""
        statuses = [('Черновик',), ('Согласован',), ('Получен',), ('Отменен',)]

        cur = self.conn.cursor()
        try:
            cur.execute("TRUNCATE TABLE purchase_status RESTART IDENTITY CASCADE")

            query = "INSERT INTO purchase_status (status) VALUES %s"
            cur.executemany(query, statuses)
            self.conn.commit()
            print(f"Добавлено {len(statuses)} статусов закупок.")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при генерации статусов закупок: {e}")
        finally:
            cur.close()

    def generate_sale_doc(self):
        generated_data = []
        for _ in range(1000):
            sale_doc = {'doc_date': self.faker.date_time_between(start_date='2025-01-01', end_date='2025-12-31'),
                        'currency_id': random.choice(self.get_id_from_table('currency')),
                        'store_id': random.choice(self.get_id_from_table('store')),
                        'status_id': random.choice(self.get_id_from_table('sale_status'))}
            record = (sale_doc['doc_date'], sale_doc['currency_id'], sale_doc['store_id'], sale_doc['status_id'])
            generated_data.append(record)

        query = """INSERT INTO sale_doc (doc_date, currency, store_id, status) VALUES %s"""
        self._execute_batch(query, generated_data)

    def generate_purchase_doc(self):
        generated_data = []
        for _ in range(1000):
            purchase_doc = {'doc_date': self.faker.date_time_between(start_date='2025-01-01', end_date='2025-12-31'),
                        'currency_id': random.choice(self.get_id_from_table('currency')),
                        'store_id': random.choice(self.get_id_from_table('store')),
                        'supplier_id': random.choice(self.get_id_from_table('supplier')),
                        'status_id': random.choice(self.get_id_from_table('purchase_status'))}
            record = (purchase_doc['doc_date'], purchase_doc['currency_id'], purchase_doc['store_id'],
                      purchase_doc['supplier_id'], purchase_doc['status_id'])
            generated_data.append(record)

        query = """INSERT INTO purchase_doc (doc_date, currency, store_id, supplier_id, status) VALUES %s"""
        self._execute_batch(query, generated_data)

    def generate_purchase_items(self, items_per_doc: int = 5):

        generated_data = []
        doc_ids = self.get_id_from_table('purchase_doc')
        if not doc_ids:
            logger.error("Таблица purchase_doc пуста. Сначала создайте документы.")
            return

        for _ in range(1000):  # Количество строк в таблице items
            record = (
                self.faker.random_element(doc_ids),
                random.choice(self.get_id_from_table('product')),
                round(self.faker.pyfloat(min_value=10, max_value=5000), 2),
                self.faker.random_int(min_value=1, max_value=50),
                random.choice(self.get_id_from_table('tax_rate'))
            )
            generated_data.append(record)

        query = """
            INSERT INTO purchase_item (doc_number_id, product_id, price, quantity, tax_id) 
            VALUES %s
        """
        self._execute_batch(query, generated_data)

    def generate_sale_items(self, items_count: int = 1000):
        """
        Генерация позиций продаж.
        Цены берем из product.current_price с небольшой вариацией.
        """
        # 🔥 1. Кэшируем данные: один запрос вместо 1000
        product_prices = self._get_product_prices_cache()  # {id: price}
        product_ids = list(product_prices.keys())
        tax_ids = self.get_id_from_table('tax_rate')
        doc_ids = self.get_id_from_table('sale_doc')  # ✅ Исправлено: sale_doc, не sales_doc

        if not all([product_prices, tax_ids, doc_ids]):
            logger.error("Заполните справочники product, tax_rate, sale_doc")
            return

        generated_data = []

        for _ in range(items_count):
            product_id = random.choice(product_ids)
            base_price = product_prices[product_id]

            # 🔥 2. Добавляем реалистичность: цена ±10% от базовой
            sale_price = round(base_price * random.uniform(0.9, 1.1), 2)

            record = (
                random.choice(doc_ids),  # doc_number_id
                product_id,  # product_id
                sale_price,  # price (из кэша с вариацией)
                self.faker.random_int(min_value=1, max_value=50),  # quantity
                random.choice(tax_ids)  # tax_id
            )
            generated_data.append(record)

        # ✅ Исправлено: вставляем в sale_item, не purchase_item
        query = """
            INSERT INTO sale_item (doc_number_id, product_id, price, quantity, tax_id) 
            VALUES %s
        """
        self._execute_batch(query, generated_data)
        logger.info(f"Сгенерировано {len(generated_data)} позиций продаж")

    def _get_product_prices_cache(self) -> dict:
        """
        Вспомогательный метод: загружает {product_id: current_price} один раз.
        """
        if not self.conn:
            return {}

        cur = self.conn.cursor()
        try:
            # Загружаем ВСЕ товары с ценами одним запросом
            cur.execute("SELECT id, current_price FROM product WHERE current_price IS NOT NULL")
            return {row[0]: float(row[1]) for row in cur.fetchall()}
        except Exception as e:
            logger.error(f"Ошибка загрузки цен: {e}")
            return {}
        finally:
            cur.close()
