--Таблица по кадому магазину
CREATE TABLE store (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200) NOT NULL,
	city VARCHAR(100) NOT NULL,
	street VARCHAR(200) NOT NULL,
	phone VARCHAR(20),
	is_active BOOLEAN NOT NULL defaul True);

--Таблица по каждому поставщику
CREATE TABLE supplier (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100),
	inn VARCHAR(30),
	address VARCHAR(200),
	contact_mail VARCHAR(100),
	created_at TIMESTAMP default NOW()
	is_active BOOLEAN NOT NULL default True);

--Таблица с информацией по товару
CREATE TABLE product (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	current_price DECIMAL(12,2),
	category_id INT REFERENCES categories(id),
	brand VARCHAR(100),
	uom VARCHAR 100 REFERENCES uom(id),
	created_at TIMESTAMP default NOW(),
	is_active default True);

--Название конкурента
CREATE TABLE competitor (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200));

--История цен конкурентов
CREATE TABLE competitor_price (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200)
	competitor_id REFERENCES competitor(id),
	product_id REFERENCES product(id),
	reg_price DECIMAL(12,2),
	promo_price DECIMAL(12,2),
	scraped_at TIMESTAMP default NOW(),
	source_url VARCHAR(500))
	;


--Цена товара на дату
CREATE TABLE product_price_history (
	id SERIAL PRIMARY KEY,
	product_id INT REFERENCES product(id),
	reg_price DECIMAL(12,2) NOT NULL,
	promo_price DECIMAL(12,2),
	valid_from TIMESTAMP DEFAULT NOW(),
	valid_to TIMESTAMP);


--Таблица по категориям продающимся в сети
CREATE TABLE categories (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200),
	parent_id INT,
	level_id INT);


--Единицы измерения
CREATE TABLE uom (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100));
	
--Справочник таблицы по налогам и ставкам
CREATE TABLE tax_rate (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100),
	rate INT);
	

--Справочник валюта
CREATE TABLE currency (
	id SERIAL PRIMARY KEY,
	name VARCHAR(20));
	


CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100))
	
	
--Таблица по каждому складу
CREATE TABLE warehouse (
	id SERIAL PRIMARY KEY,
	warehouse VARCHAR(100),
	store_id INT NOT NULL REFERENCES shop(id),
	phone VARCHAR(20),
	);


--Таблица закупок по каждому документу
CREATE TABLE purchase_doc (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES shop(id),
	supplier_id INT NOT NULL REFERENCES supplier(id),
	status VARCHAR(100) CHECK (status in('draft', 'opened', 'closed')),
	create_at DATE NOT NULL default CURRENT_DATE);


CREATE TABLE purchase_item (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200));


CREATE TABLE sale (
	id SERIAL PRIMARY KEY,
	doc_number VARCHAR(200) NOT NULL UNIQUE,
	doc_date TIMESTAMP NOT NULL,
	currency INT NOT NULL REFERENCES currency(id),
	store_id INT NOT NULL REFERENCES shop(id),
	status VARCHAR(100) CHECK (status in('draft', 'opened', 'closed')),
	create_at DATE NOT NULL default CURRENT_DATE);


CREATE TABLE sale_item (
	id SERIAL PRIMARY KEY,
	name VARCHAR(200));



CREATE TABLE movement (
id SERIAL PRIMARY KEY,
name VARCHAR(200));




















