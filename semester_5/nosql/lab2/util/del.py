from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import psycopg2


async def clear_mongo_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]

    # Очистка всех коллекций
    await db["projects"].delete_many({})
    await db["proposals"].delete_many({})
    await db["messages"].delete_many({})

    print("Все проекты, предложения и сообщения удалены из MongoDB.")


asyncio.run(clear_mongo_data())


def clear_sql_data():
    # Подключение к базе данных
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Удаление всех сообщений
    cursor.execute("DELETE FROM messages WHERE contract_id IS NOT NULL;")

    # Удаление всех предложений
    cursor.execute("DELETE FROM proposals WHERE project_id IS NOT NULL;")

    # Удаление всех контрактов
    cursor.execute("DELETE FROM contracts WHERE contract_id IS NOT NULL;")

    # Удаление всех проектов
    cursor.execute("DELETE FROM projects WHERE project_id IS NOT NULL;")



    # Завершаем транзакцию
    conn.commit()

    print("Все проекты, предложения и сообщения удалены из PostgreSQL.")

    cursor.close()
    conn.close()


clear_sql_data()
