import faker

faker = faker.Faker(locale='Ru')
sales = []

for _ in range(20):
    data = {"Название": faker.name(),
            "Рег_цена": faker.name(),
            "Цена": faker.name(),
            "Бренд": faker.name(),
            "sku": faker.name(),
            "Дата": faker.name(),
            "Прокси": faker.name(),
            "Ошибка": faker.name(),
            "URL": faker.name()
            }
    sales.append(data)
    print(data)
