import faker
import psycopg
import pandas as pd

class OltpDataGenerator:
    def __init__(self):
        self.faker = faker.Faker(locale='ru_RU')
        self.conn = psycopg.connect(
            host="localhost",
            dbname="oltp_test",
            user="postgres",
            password='1'
        )
    def generate_store(self):
        cur = self.conn.cursor()
        generated_data = []
        for _ in range(15):
            store = {'name': f"ГИП{self.faker.random_int(min=1, max=100)}",
                        'city': self.faker.city(),
                        'street': self.faker.address(),
                        'phone': self.faker.phone_number(),
                        'is_active': self.faker.boolean()
            }
            record = (store['name'], store['city'], store['street'], store['phone'], store['is_active'])
            generated_data.append(record)
        try:
            cur.executemany(""" INSERT INTO store (name, city, street, phone, is_active)
             VALUES (%s, %s, %s, %s, %s) """, generated_data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()


    def generate_competitors(self):
        cur = self.conn.cursor()
        try:
            cur.execute(""" INSERT INTO competitor (name) VALUES ('ozon') """)
            cur.execute(""" INSERT INTO competitor (name) VALUES ('maxidom') """)
            self.conn.commit()
            print("Все данные сохранены")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()

    def generate_supplier(self):
        cur = self.conn.cursor()
        generated_data = []
        for _ in range(20):
            supplier = {'name': self.faker.company(),
                        'inn': self.faker.random_number(digits=10),
                        'address': self.faker.address(),
                        'email': self.faker.email(),
                        'is_active': self.faker.boolean()
            }
            record = (supplier['name'], supplier['inn'], supplier['address'], supplier['email'], supplier['is_active'])
            generated_data.append(record)
        try:
            cur.executemany(""" INSERT INTO supplier (name, inn, address, email, is_active)
             VALUES (%s, %s, %s, %s, %s) """, generated_data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()


    def generate_currency(self):
        cur = self.conn.cursor()
        try:
            cur.execute(""" INSERT INTO currency (name) VALUES ('RUB') """)
            cur.execute(""" INSERT INTO currency (name) VALUES ('USD') """)
            cur.execute(""" INSERT INTO currency (name) VALUES ('CNY') """)
            self.conn.commit()
            print("Все данные сохранены")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()

    def generate_uom(self):
        cur = self.conn.cursor()
        try:
            cur.execute(""" INSERT INTO uom (name) VALUES ('шт') """)
            cur.execute(""" INSERT INTO uom (name) VALUES ('уп') """)
            cur.execute(""" INSERT INTO uom (name) VALUES ('м') """)
            self.conn.commit()
            print("Все данные сохранены")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()

    def generate_tax_rate(self):
        cur = self.conn.cursor()
        try:
            cur.execute(""" INSERT INTO tax_rate (name, rate) VALUES ('НДС', '22') """)
            self.conn.commit()
            print("Все данные сохранены")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()

    def generate_categories(self):
        cur = self.conn.cursor()
        df = pd.read_excel('product_matrix.xlsx')['УК'].unique().tolist()
        record = [(elem, None, elem[1:3]) for elem in df]
        try:
            cur.executemany("""INSERT INTO categories (name, level_id) VALUES (%s, %s)""", record)
            self.conn.commit()
            print("Все данные сохранены")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка: {e}")
        finally:
            cur.close()




