-- Схема навчальної БД інтернет-магазину.
-- Виконується автоматично при першому запуску контейнера PostgreSQL.

CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    full_name  TEXT        NOT NULL,
    email      TEXT        NOT NULL UNIQUE,
    city       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id    SERIAL PRIMARY KEY,
    name  TEXT          NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    stock INTEGER       NOT NULL CHECK (stock >= 0)
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER       NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id  INTEGER       NOT NULL REFERENCES products(id),
    quantity    INTEGER       NOT NULL CHECK (quantity > 0),
    total       NUMERIC(12,2) NOT NULL,
    -- new -> paid -> shipped -> delivered, або cancelled
    status      TEXT          NOT NULL DEFAULT 'new',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX orders_customer_idx  ON orders(customer_id);
-- Пошук найстарішого/найновішого замовлення з певним статусом без перебору таблиці
CREATE INDEX orders_status_id_idx ON orders(status, id);
-- Звіт за останню годину
CREATE INDEX orders_created_idx   ON orders(created_at);

INSERT INTO products (name, price, stock) VALUES
    ('Ноутбук',            32999.00, 200),
    ('Смартфон',           18499.00, 300),
    ('Навушники',           2499.00, 500),
    ('Монітор 27"',         9999.00, 150),
    ('Клавіатура',          1599.00, 400),
    ('Миша',                 799.00, 600),
    ('Зовнішній SSD 1 ТБ',  3899.00, 250),
    ('Вебкамера',           1899.00, 300),
    ('Роутер Wi-Fi',        2799.00, 200),
    ('Павербанк',           1299.00, 500);

INSERT INTO customers (full_name, email, city) VALUES
    ('Тарас Шевченко',   'taras@example.com',  'Київ'),
    ('Леся Українка',    'lesya@example.com',  'Луцьк'),
    ('Іван Франко',      'ivan@example.com',   'Львів');
