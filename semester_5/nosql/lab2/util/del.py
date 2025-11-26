from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import psycopg2


async def clear_mongo_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]

    # Очищення всіх колекцій
    await db["projects"].delete_many({})
    await db["proposals"].delete_many({})
    await db["messages"].delete_many({})

    print("Всі проекти, пропозиції та повідомлення видалені з MongoDB.")


asyncio.run(clear_mongo_data())


def clear_sql_data():
    # Підключення до бази даних
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Видалення всіх повідомлень
    cursor.execute("DELETE FROM messages WHERE contract_id IS NOT NULL;")

    # Видалення всіх пропозицій
    cursor.execute("DELETE FROM proposals WHERE project_id IS NOT NULL;")

    # Видалення всіх контрактів
    cursor.execute("DELETE FROM contracts WHERE contract_id IS NOT NULL;")

    # Видалення всіх проектів
    cursor.execute("DELETE FROM projects WHERE project_id IS NOT NULL;")

    # Завершуємо транзакцію
    conn.commit()

    print("Всі проекти, пропозиції та повідомлення видалені з PostgreSQL.")

    cursor.close()
    conn.close()


clear_sql_data()
