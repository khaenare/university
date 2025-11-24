import os
import psycopg2
from dotenv import load_dotenv

# ==============================
# Підключення до PostgreSQL
# ==============================

# Завантажуємо змінні середовища з .env (якщо файл існує)
load_dotenv()


def get_connection():
    """
    Отримати нове підключення до БД PostgreSQL.

    За замовчуванням орієнтуємось на локальний Postgres.app:
    - база: template1
    - користувач: matvii
    - порт: 5432

    У разі потреби ці значення можна змінити через змінні середовища:
    DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
    """
    db_name = os.getenv("DB_NAME", "template1")
    db_user = os.getenv("DB_USER", "matvii")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    return connection
