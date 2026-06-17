-- Очистка таблиц перед созданием
DROP TABLE IF EXISTS receipt_items CASCADE;
DROP TABLE IF EXISTS receipts CASCADE;
DROP TABLE IF EXISTS menu CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS list_of_tables CASCADE;

-- Создание таблиц-справочников
CREATE TABLE menu (
    item_id UUID PRIMARY KEY,
    category VARCHAR(20),
    dish_name VARCHAR(100),
    price NUMERIC(10, 2),
    popularity_weight INT
);

CREATE TABLE staff (
    staff_id UUID PRIMARY KEY,
    staff_name VARCHAR(50),
    staff_position VARCHAR(30)
);

CREATE TABLE list_of_tables (
    table_id INT PRIMARY KEY,
    zone_name VARCHAR(50),
    capacity INT
);

CREATE TABLE clients (
    client_id UUID PRIMARY KEY,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    registration_date DATE,
    loyalty_level VARCHAR(20)	
);

-- Создание таблиц фактов
CREATE TABLE receipts (
    receipt_id UUID PRIMARY KEY,
    receipt_time TIMESTAMP,
    staff_id UUID REFERENCES staff(staff_id),
    table_id INT REFERENCES list_of_tables(table_id),
    client_id UUID REFERENCES clients(client_id),
    total_price NUMERIC(10, 2),
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    final_price DECIMAL(10, 2)
);

CREATE TABLE receipt_items (
    receipt_id UUID REFERENCES receipts(receipt_id),
    item_id UUID REFERENCES menu(item_id),
    quantity INT,
    price_per_item NUMERIC(10, 2),
    total_price NUMERIC(10, 2),
    PRIMARY KEY (receipt_id, item_id)
);