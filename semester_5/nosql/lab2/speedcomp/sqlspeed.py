import psycopg2
import time


def insert_sql_data():
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    start_time = time.time()

    # Вставляємо 10000 проектів і потім вставляємо пропозиції з правильним project_id
    for i in range(100000):
        client_id = 1  # Обов'язкове поле, вказуємо client_id
        cursor.execute("""
                       INSERT INTO projects (client_id, category_id, title, description, budget_min, budget_max, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING project_id;
                       """, (client_id, 1, f"Project {i}", "Project description", 5000, 10000, "open"))

        # Отримуємо повернуте project_id
        project_id = cursor.fetchone()[0]

        # Вставляємо пропозицію з правильним project_id
        cursor.execute("""
                       INSERT INTO proposals (project_id, freelancer_id, cover_letter, bid_amount, status)
                       VALUES (%s, %s, %s, %s, %s) RETURNING proposal_id;
                       """, (project_id, 1, "Cover letter", 1000, "pending"))

        # Отримуємо proposal_id для створення контракту
        proposal_id = cursor.fetchone()[0]

        # Створюємо контракт для кожної пропозиції
        cursor.execute("""
                       INSERT INTO contracts (project_id, client_id, freelancer_id, start_date, status, fixed_price,
                                              created_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING contract_id;
                       """, (project_id, client_id, 1, "2025-11-01", "active", 1000.0, client_id))

        # Отримуємо contract_id для вставки повідомлень
        contract_id = cursor.fetchone()[0]

        # Вставляємо повідомлення з правильним contract_id
        cursor.execute("""
                       INSERT INTO messages (contract_id, sender_id, receiver_id, body, sent_at, is_read, is_deleted)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       """, (contract_id, 1, 2, "Message body", "2025-11-26T12:00:00Z", False, False))

    conn.commit()
    end_time = time.time()

    print(f"Час, витрачений на вставку 10,000 записів у PostgreSQL: {end_time - start_time} секунд")

    cursor.close()
    conn.close()


insert_sql_data()

def fetch_sql_data():
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    start_time = time.time()

    # Отримуємо всі проекти
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    end_time = time.time()
    print(f"Час, витрачений на отримання всіх проектів з PostgreSQL: {end_time - start_time} секунд")

    cursor.close()
    conn.close()

fetch_sql_data()
