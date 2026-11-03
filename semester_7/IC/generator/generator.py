"""
Генератор навантаження на БД інтернет-магазину.

Безперервно виконує типові операції з БД (реєстрація клієнтів, оформлення
та оновлення замовлень, звіти, очищення) і для кожної операції:
  * оновлює метрики для Prometheus (кількість, тривалість, помилки);
  * пише структурований JSON-лог у stdout (його збирає Alloy і відправляє в Loki);
  * створює трейс у Tempo (дочірні span'и — окремі SQL-запити).
"""
import json
import logging
import os
import random
import signal
import sys
import time
import uuid
from datetime import datetime, timezone

import psycopg2
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, start_http_server

SERVICE_NAME = "generator"
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "dbname": os.getenv("DB_NAME", "shop"),
    "user": os.getenv("DB_USER", "shop"),
    "password": os.getenv("DB_PASSWORD", ""),
    # Не чекати безкінечно на заблоковані рядки/таблиці: краще помилка в логах і метриках
    "options": "-c lock_timeout=3s -c statement_timeout=10s",
}
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
# Пауза між операціями, секунди
MIN_DELAY = float(os.getenv("MIN_DELAY", "0.1"))
MAX_DELAY = float(os.getenv("MAX_DELAY", "0.5"))


# ---------- Логи: JSON з trace_id, щоб з логу перейти до трейсу ----------

class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            # ISO 8601 з часовим поясом, щоб не плутати з локальним часом у Grafana
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        ctx = trace.get_current_span().get_span_context()
        if ctx.is_valid:
            entry["trace_id"] = format(ctx.trace_id, "032x")
        return json.dumps(entry, ensure_ascii=False, default=str)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger(SERVICE_NAME)


def error_text(exc):
    """Короткий опис помилки для логу: тип і перший рядок повідомлення."""
    lines = str(exc).strip().splitlines()
    return f"{type(exc).__name__}: {lines[0]}" if lines else type(exc).__name__


# ---------- Метрики для Prometheus ----------

OPERATIONS_TOTAL = Counter(
    "generator_operations", "Кількість виконаних операцій з БД",
    ["operation", "status"],
)
OPERATION_DURATION = Histogram(
    "generator_operation_duration_seconds", "Тривалість операцій з БД, с",
    ["operation"],
    # Дрібніші межі в діапазоні 0.5–2 с, де працює slow_report, щоб p95 не завищувався
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 5),
)


# ---------- Трейси для Tempo ----------

def setup_tracing():
    provider = TracerProvider(resource=Resource.create({"service.name": SERVICE_NAME}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT)))
    trace.set_tracer_provider(provider)
    # Кожен SQL-запит через psycopg2 автоматично стає окремим span'ом
    Psycopg2Instrumentor().instrument(skip_dep_check=True)


tracer = trace.get_tracer(SERVICE_NAME)


# ---------- Операції з БД ----------

FIRST_NAMES = ["Олександр", "Марія", "Іван", "Олена", "Андрій", "Наталія",
               "Дмитро", "Ірина", "Сергій", "Юлія", "Максим", "Анна"]
LAST_NAMES = ["Шевченко", "Коваленко", "Бондаренко", "Ткаченко", "Кравченко",
              "Мельник", "Олійник", "Поліщук", "Савченко", "Руденко"]
CITIES = ["Київ", "Львів", "Харків", "Одеса", "Дніпро", "Запоріжжя",
          "Вінниця", "Полтава", "Чернігів", "Ужгород"]


def create_customer(cur):
    """Реєстрація нового клієнта."""
    cur.execute(
        "INSERT INTO customers (full_name, email, city) VALUES (%s, %s, %s) RETURNING id",
        (f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
         f"user-{uuid.uuid4().hex[:12]}@example.com",
         random.choice(CITIES)),
    )
    return {"customer_id": cur.fetchone()[0]}


def random_customer(cur):
    """Випадковий клієнт через пошук по первинному ключу (без ORDER BY random() по всій таблиці)."""
    cur.execute("SELECT min(id), max(id) FROM customers")
    low, high = cur.fetchone()
    if low is None:
        raise LookupError("у таблиці customers немає жодного клієнта")
    cur.execute("SELECT id FROM customers WHERE id >= %s ORDER BY id LIMIT 1",
                (random.randint(low, high),))
    return cur.fetchone()[0]


def create_order(cur):
    """Оформлення замовлення: списання товару зі складу і запис замовлення."""
    customer_id = random_customer(cur)
    # Товарів лише 10, тому ORDER BY random() тут дешевий
    cur.execute("SELECT id, price FROM products ORDER BY random() LIMIT 1 FOR UPDATE")
    product_id, price = cur.fetchone()
    quantity = random.randint(1, 5)
    # Якщо товару не вистачає — спрацює CHECK (stock >= 0) і транзакція відкотиться
    cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
    cur.execute(
        "INSERT INTO orders (customer_id, product_id, quantity, total) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (customer_id, product_id, quantity, price * quantity),
    )
    return {"order_id": cur.fetchone()[0], "customer_id": customer_id,
            "product_id": product_id, "quantity": quantity}


NEXT_STATUS = {"new": "paid", "paid": "shipped", "shipped": "delivered"}


def update_order_status(cur):
    """Обробка замовлень: на кожному етапі (new -> paid -> shipped -> delivered)
    найстаріше замовлення переходить далі, тож замовлення не накопичуються в 'new'."""
    moved = 0
    # Від останнього етапу до першого, щоб одне замовлення не пройшло всі етапи за раз
    for status, next_status in reversed(NEXT_STATUS.items()):
        # Індекс (status, id) дає змогу знайти замовлення без перебору всієї таблиці
        cur.execute("""
            UPDATE orders SET status = %s
            WHERE id = (SELECT id FROM orders WHERE status = %s ORDER BY id LIMIT 1)
        """, (next_status, status))
        moved += cur.rowcount
    return {"orders_moved": moved}


def cancel_order(cur):
    """Скасування найновішого замовлення зі статусом new з поверненням товару на склад."""
    cur.execute("""
        UPDATE orders SET status = 'cancelled'
        WHERE id = (SELECT id FROM orders WHERE status = 'new' ORDER BY id DESC LIMIT 1)
        RETURNING id, product_id, quantity
    """)
    row = cur.fetchone()
    if row is None:
        return {}
    cur.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (row[2], row[1]))
    return {"order_id": row[0]}


def restock(cur):
    """Поповнення складу товаром, якого залишилось найменше."""
    cur.execute("""
        UPDATE products SET stock = stock + %s
        WHERE id = (SELECT id FROM products ORDER BY stock LIMIT 1)
        RETURNING id, stock
    """, (random.randint(20, 80),))
    product_id, stock = cur.fetchone()
    return {"product_id": product_id, "stock": stock}


def sales_report(cur):
    """Аналітичний запит: кількість оплачених замовлень і виручка за містами за останню годину."""
    cur.execute("""
        SELECT c.city, count(*), sum(o.total)
        FROM orders o JOIN customers c ON c.id = o.customer_id
        WHERE o.status IN ('paid', 'shipped', 'delivered')
          AND o.created_at > now() - interval '1 hour'
        GROUP BY c.city ORDER BY 3 DESC
    """)
    return {"cities": len(cur.fetchall())}


def slow_report(cur):
    """Імітація важкого запиту (> 300 мс) — потрапляє в лог повільних запитів PostgreSQL."""
    cur.execute("SELECT pg_sleep(%s), count(*) FROM orders",
                (round(random.uniform(0.3, 1.2), 2),))
    return {"orders_total": cur.fetchone()[1]}


def delete_cancelled(cur):
    """Очищення: видалення скасованих замовлень, старших за 5 хвилин."""
    cur.execute("DELETE FROM orders WHERE status = 'cancelled' "
                "AND created_at < now() - interval '5 minutes'")
    return {"deleted": cur.rowcount}


def invalid_order(cur):
    """Імітація некоректного запиту: замовлення неіснуючого клієнта (порушення FOREIGN KEY)."""
    cur.execute("INSERT INTO orders (customer_id, product_id, quantity, total) "
                "VALUES (-1, 1, 1, 1)")
    return {}


# (назва, функція, вага — наскільки часто виконується).
# update_order_status просуває по одному замовленню на кожному етапі, тому його
# вага не менша за create_order — інакше нові замовлення накопичуються.
OPERATIONS = [
    ("create_customer", create_customer, 15),
    ("create_order", create_order, 30),
    ("update_order_status", update_order_status, 30),
    ("cancel_order", cancel_order, 5),
    ("restock", restock, 5),
    ("sales_report", sales_report, 7),
    ("slow_report", slow_report, 2),
    ("delete_cancelled", delete_cancelled, 3),
    ("invalid_order", invalid_order, 3),
]

# Лічильники стартують з нуля для всіх операцій, щоб rate()/increase()
# у Prometheus враховували навіть першу помилку
for op_name, _, _ in OPERATIONS:
    OPERATION_DURATION.labels(op_name)
    for op_status in ("success", "error"):
        OPERATIONS_TOTAL.labels(op_name, op_status)


def run_operation(conn, name, func):
    """Виконує одну операцію в окремій транзакції з метриками, логом і трейсом."""
    with tracer.start_as_current_span(name) as span:
        started = time.perf_counter()
        try:
            # with conn: COMMIT при успіху, ROLLBACK при помилці
            with conn, conn.cursor() as cur:
                details = func(cur)
            status, error = "success", None
        # Будь-яка помилка (не лише БД) рахується як невдала операція,
        # але не зупиняє генератор
        except Exception as exc:
            status, details = "error", {}
            error = error_text(exc)
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, error))
        duration = time.perf_counter() - started

        OPERATIONS_TOTAL.labels(name, status).inc()
        OPERATION_DURATION.labels(name).observe(duration)
        for key, value in details.items():
            span.set_attribute(f"shop.{key}", value)

        fields = {"operation": name, "status": status,
                  "duration_ms": round(duration * 1000, 1), **details}
        if error:
            log.error("Операція %s завершилась помилкою: %s", name, error,
                      extra={"fields": fields})
        else:
            log.info("Операція %s виконана", name, extra={"fields": fields})


def connect():
    """Підключення до БД з повторними спробами (СУБД може ще стартувати або бути зупинена)."""
    delay = 1
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
            log.info("Підключено до БД", extra={"fields": {"host": DB_CONFIG["host"]}})
            return conn
        except psycopg2.OperationalError as exc:
            if "password authentication failed" in str(exc):
                # Це не збій СУБД, а помилка налаштувань: паролі з .env застосовуються
                # лише при першому створенні тому pg-data
                log.error("Невірний логін або пароль до БД (перевірте APP_DB_PASSWORD у .env; "
                          "після першого запуску пароль змінюється лише через ALTER ROLE), "
                          "повтор через %s с", delay, extra={"fields": {"error": error_text(exc)}})
            else:
                log.warning("БД недоступна, повтор через %s с", delay,
                            extra={"fields": {"error": error_text(exc)}})
            time.sleep(delay)
            delay = min(delay * 2, 10)


def main():
    # docker stop надсилає SIGTERM: штатне завершення запускає обробники atexit,
    # і OpenTelemetry встигає відправити трейси, що ще лежать у буфері
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    setup_tracing()
    start_http_server(METRICS_PORT)
    log.info("Генератор запущено", extra={"fields": {"metrics_port": METRICS_PORT}})

    conn = connect()
    weights = [weight for _, _, weight in OPERATIONS]
    while True:
        name, func, _ = random.choices(OPERATIONS, weights=weights)[0]
        run_operation(conn, name, func)
        if conn.closed:
            log.warning("З'єднання з БД втрачено, перепідключення")
            conn = connect()
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


if __name__ == "__main__":
    main()
