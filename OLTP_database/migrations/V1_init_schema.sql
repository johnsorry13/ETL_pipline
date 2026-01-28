--Таблица по кадому магазину
CREATE TABLE store (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL,
	city VARCHAR(100) NOT NULL,
	street VARCHAR(200) NOT NULL,
	phone VARCHAR(15),
	is_active BOOLEAN NOT NULL default True,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);

--Таблица по каждому поставщику
CREATE TABLE supplier (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100),
	inn VARCHAR(30) UNIQUE,
	address VARCHAR(200),
	email VARCHAR(100),
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW(),
	is_active BOOLEAN NOT NULL DEFAULT TRUE
);

--Таблица с информацией по товару
CREATE TABLE product (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	current_price DECIMAL(12,2) CHECK (current_price >= 0),
	category_id INT REFERENCES categories(id),
	brand VARCHAR(100),
	uom_id INT REFERENCES uom(id),
	created_at TIMESTAMP default NOW(),
	updated_at TIMESTAMP DEFAULT NOW(),
	is_active BOOLEAN default True
);

--Название конкурента
CREATE TABLE competitor (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL UNIQUE,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);

--История цен конкурентов
CREATE TABLE competitor_price (
	id SERIAL PRIMARY KEY,
	competitor_id REFERENCES competitor(id),
	product_id REFERENCES product(id),
	reg_price DECIMAL(12,2) CHECK (reg_price  >= 0),
	promo_price DECIMAL(12,2) CHECK (promo_price >= 0),
	scraped_at TIMESTAMP default NOW(),
	source_url VARCHAR(500),
	CONSTRAINT uq_price_compet_scraped (competitor_id, product_id, scraped_at)
);

--Цена товара на дату
CREATE TABLE product_price_history (
	id SERIAL PRIMARY KEY,
	product_id INT REFERENCES product(id),
	reg_price DECIMAL(12,2) NOT NULL,
	promo_price DECIMAL(12,2),
	valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
	valid_to TIMESTAMP,
	CONSTRAINT chk_price_dates CHECK (valid_from <= valid_to OR valid_to IS NULL)
);

--Таблица по категориям продающимся в сети
CREATE TABLE categories (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL,
	parent_id INT REFERENCES categories(id),
	level_id INT,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);

--Единицы измерения
CREATE TABLE uom (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);
	
--Справочник таблицы по налогам и ставкам
CREATE TABLE tax_rate (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	rate DECIMAL(5,2) NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);
	
--Справочник валюта
CREATE TABLE currency (
	id SERIAL PRIMARY KEY,
	name VARCHAR(20) NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);
	
--Cправочник работники
CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);
	
--Таблица по каждому складу
CREATE TABLE warehouse (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	store_id INT NOT NULL REFERENCES store(id),
	phone VARCHAR(20),
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE doc_status (
	id SERIAL PRIMARY KEY,
	status VARCHAR(50) NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);


--Таблица закупок по каждому документу
CREATE TABLE purchase_doc (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	supplier_id INT NOT NULL REFERENCES supplier(id),
	status INT NOT NULL REFERENCES doc_status(id),
	create_at DATE NOT NULL default CURRENT_DATE,
	CONSTRAINT uq_doc_shop UNIQUE (doc_number, store_id)
);

--Таблица закупки попозиционно
CREATE TABLE purchase_item (
	id SERIAL PRIMARY KEY,
	doc_number_id INT NOT NULL REFERENCES purchase_doc(id),
	product_id INT NOT NULL REFERENCES product(id),
	price DECIMAL(12,2) NOT NULL,
	quantity INT NOT NULL CHECK (quantity > 0),
	tax_id INT REFERENCES tax_rate(id)
);



CREATE TABLE sale (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	status VARCHAR(100) CHECK (status in('draft', 'opened', 'closed')),
	create_at TIMESTAMP NOT NULL default NOW(),
	CONSTRAINT uq_doc_shop UNIQUE (doc_number, store_id)
);


CREATE TABLE sale_item (
	id SERIAL PRIMARY KEY,
	doc_number_id INT NOT NULL REFERENCES sale(id),
	product_id INT NOT NULL REFERENCES product(id),
	price DECIMAL(12,2) NOT NULL,
	quantity INT NOT NULL CHECK (quantity > 0),
	tax_id INT REFERENCES tax_rate(id)
);




















