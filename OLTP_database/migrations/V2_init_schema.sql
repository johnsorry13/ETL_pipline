--Таблица по кадому магазину
CREATE TABLE store (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL,
	city VARCHAR(100) NOT NULL,
	street VARCHAR(200) NOT NULL,
	phone VARCHAR(15),
	is_active BOOLEAN NOT NULL default True,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--Таблица по каждому поставщику
CREATE TABLE supplier (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL UNIQUE,
	inn VARCHAR(30) UNIQUE,
	address VARCHAR(200),
	email VARCHAR(100),
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
	is_active BOOLEAN NOT NULL DEFAULT TRUE
);

--Справочник валюта
CREATE TABLE currency (
	id SERIAL PRIMARY KEY,
	name VARCHAR(20) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
	
--Таблица по категориям продающимся в сети
CREATE TABLE categories (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL,
	parent_id INT REFERENCES categories(id),
	level_id INT,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--Единицы измерения
CREATE TABLE uom (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--Справочник таблицы по налогам и ставкам
CREATE TABLE tax_rate (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	rate DECIMAL(5,2) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--Cправочник работники
CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


--Таблица с информацией по товару
CREATE TABLE product (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL UNIQUE,
	current_price DECIMAL(12,2) CHECK (current_price >= 0),
	category_id INT REFERENCES categories(id),
	brand VARCHAR(100) NOT NULL,
	uom_id INT REFERENCES uom(id),
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
	is_active BOOLEAN default True
);

--Название конкурента
CREATE TABLE competitor (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL UNIQUE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--История цен конкурентов
CREATE TABLE competitor_price (
	id SERIAL PRIMARY KEY,
	competitor_id INT REFERENCES competitor(id),
	product_id INT REFERENCES product(id),
	reg_price DECIMAL(12,2) CHECK (reg_price  >= 0),
	promo_price DECIMAL(12,2) CHECK (promo_price >= 0),
	scraped_at TIMESTAMP default NOW(),
	source_url VARCHAR(500),
	CONSTRAINT uq_price_compet_scraped UNIQUE (competitor_id, product_id, scraped_at)
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
	
--Таблица по каждому складу
CREATE TABLE warehouse (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	store_id INT NOT NULL REFERENCES store(id),
	phone VARCHAR(20),
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE purchase_status (
	id SERIAL PRIMARY KEY,
	status VARCHAR(50) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


--Таблица закупок по каждому документу
CREATE TABLE purchase_doc (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	supplier_id INT NOT NULL REFERENCES supplier(id),
	status INT NOT NULL REFERENCES purchase_status(id),
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	CONSTRAINT uq_prch_doc_shop UNIQUE (doc_number, store_id)
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

CREATE TABLE sale_status (
	id SERIAL PRIMARY KEY,
	status VARCHAR(50) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--Таблица продаж по каждому документу
CREATE TABLE sale (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	status INT NOT NULL REFERENCES sale_status(id),
	created_at TIMESTAMP NOT NULL default NOW(),
	CONSTRAINT uq_sale_doc_shop UNIQUE (doc_number, store_id)
);


--Таблица продажи попозиционно
CREATE TABLE sale_item (
	id SERIAL PRIMARY KEY,
	doc_number_id INT NOT NULL REFERENCES sale(id),
	product_id INT NOT NULL REFERENCES product(id),
	price DECIMAL(12,2) NOT NULL,
	quantity INT NOT NULL CHECK (quantity > 0),
	tax_id INT REFERENCES tax_rate(id)
);
--Таблица для актуальных остатков

CREATE TABLE stock (
	id SERIAL PRIMARY KEY,
	warehouse_id INT NOT NULL REFERENCES warehouse(id),
	product_id INT NOT NULL REFERENCES product(id),
	physical_qty DECIMAL(12,2) NOT NULL CHECK (physical_qty >= 0),
	reserved_qty DECIMAL(12,2) NOT NULL CHECK (reserved_qty >= 0),
	avg_cost DECIMAL(12,2) NOT NULL CHECK (avg_cost >= 0),
	created_at TIMESTAMP DEFAULT NOW() NOT NULL,
	updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
	CONSTRAINT uq_prd_wh UNIQUE(product_id, warehouse_id),
	CHECK (reserved_qty <= physical_qty)
	);

	CREATE INDEX idx_stock_warehouse_product ON stock (warehouse_id, product_id);
	
CREATE TABLE operation_type (
	code VARCHAR(100) PRIMARY KEY NOT NULL,
	name VARCHAR(100),
	description VARCHAR (200)
	);



CREATE TABLE stock_history (
	id SERIAL PRIMARY KEY,
	warehouse_id INT NOT NULL REFERENCES warehouse(id),
	product_id INT NOT NULL REFERENCES product(id),
	
	old_physical_qty DECIMAL(12,2) NOT NULL CHECK (old_physical_qty >= 0),
    old_reserved_qty DECIMAL(12,2) NOT NULL CHECK (old_reserved_qty >= 0),
    old_avg_cost DECIMAL(12,2) NOT NULL CHECK (old_avg_cost >= 0),
    
	new_physical_qty DECIMAL(12,2) NOT NULL CHECK (new_physical_qty >= 0),
	new_reserved_qty DECIMAL(12,2) NOT NULL CHECK (new_reserved_qty >= 0),
	new_avg_cost DECIMAL(12,2) NOT NULL CHECK (new_avg_cost >= 0),
	
	operation_type VARCHAR(100) REFERENCES operation_type(code),
	
	created_at TIMESTAMP DEFAULT NOW() NOT NULL,
	updated_at TIMESTAMP DEFAULT NOW() NOT NULL

	);




















