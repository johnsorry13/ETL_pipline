--Таблица по каждому магазину
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

CREATE TABLE purchase_status (
	id SERIAL PRIMARY KEY,
	status VARCHAR(50) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


--Таблица закупок по каждому документу
CREATE TABLE purchase_doc (
	id SERIAL PRIMARY KEY,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	supplier_id INT NOT NULL REFERENCES supplier(id),
	status INT NOT NULL REFERENCES purchase_status(id),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
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
CREATE TABLE sale_doc (
	id SERIAL PRIMARY KEY,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES store(id),
	status INT NOT NULL REFERENCES sale_status(id),
	created_at TIMESTAMP NOT NULL default NOW()
);


--Таблица продажи попозиционно
CREATE TABLE sale_item (
	id SERIAL PRIMARY KEY,
	doc_number_id INT NOT NULL REFERENCES sale_doc(id),
	product_id INT NOT NULL REFERENCES product(id),
	price DECIMAL(12,2) NOT NULL,
	quantity INT NOT NULL CHECK (quantity > 0),
	tax_id INT REFERENCES tax_rate(id)
);
--Таблица для актуальных остатков

CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    store_id INT NOT NULL REFERENCES store(id),
    product_id INT NOT NULL REFERENCES product(id),
    physical_qty DECIMAL(12,2) NOT NULL CHECK (physical_qty >= 0),
    reserved_qty DECIMAL(12,2) NOT NULL CHECK (reserved_qty >= 0),
    avg_cost DECIMAL(12,2) NOT NULL CHECK (avg_cost >= 0),
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT uq_prd_wh UNIQUE(product_id, store_id),
    CHECK (reserved_qty <= physical_qty)
);

CREATE TABLE operation_type (
	id SERIAL PRIMARY KEY NOT NULL,
	name VARCHAR(100),
	description VARCHAR (200)
	);


CREATE TABLE stock_history (
    id SERIAL PRIMARY KEY,
    store_id INT NOT NULL REFERENCES store(id),
    product_id INT NOT NULL REFERENCES product(id),
    operation_type INT REFERENCES operation_type(id),
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    quantity_change DECIMAL(12,2) NOT NULL, -- Положительное (приход) или отрицательное (расход)
    doc_id INT, -- Ссылка на документ (purchase_doc.id или sale_doc.id)
    price DECIMAL(12,2) DEFAULT 0
);

-- Триггеры
CREATE OR REPLACE FUNCTION updated_at_tg()
RETURNS TRIGGER AS
$$
BEGIN
	NEW.updated_at := NOW();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_catogories_updated_at
BEFORE UPDATE ON categories
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_competitor_updated_at
BEFORE UPDATE ON competitor
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_currency_updated_at
BEFORE UPDATE ON currency
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_empl_updated_at
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_product_updated_at
BEFORE UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_purch_updated_at
BEFORE UPDATE ON purchase_status
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_sale_statust_updated_at
BEFORE UPDATE ON sale_status
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_stock_updated_at
BEFORE UPDATE ON stock
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_st_hist_updated_at
BEFORE UPDATE ON stock_history
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_store_updated_at
BEFORE UPDATE ON store
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_supplier_updated_at
BEFORE UPDATE ON supplier
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_tax_rate_updated_at
BEFORE UPDATE ON tax_rate
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_uomt_updated_at
BEFORE UPDATE ON uom
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_product_price_history_updated_at
BEFORE UPDATE ON product_price_history
FOR EACH ROW
EXECUTE FUNCTION updated_at_tg();












