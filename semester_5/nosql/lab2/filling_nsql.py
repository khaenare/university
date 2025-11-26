import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


# Функція для підключення до MongoDB
async def get_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    return client["freelance_platform"]


# Функція для вставки нового проекту
async def insert_project():
    db = await get_db()
    projects_collection = db["projects"]

    # Приклад нового проекту
    new_project = {
        "title": "Розробка веб-сайту",
        "description": "Проект для створення корпоративного сайту",
        "budget": 5000,
        "skills_required": ["Python", "Django", "PostgreSQL"],
        "client_id": 1,  # Посилання на користувача
        "status": "open"
    }

    result = await projects_collection.insert_one(new_project)
    print(f"Проект додано з ID: {result.inserted_id}")


# Функція для вставки пропозицій
async def insert_proposal():
    db = await get_db()
    proposals_collection = db["proposals"]

    # Приклад пропозиції
    new_proposal = {
        "project_id": 1,
        "freelancer_id": 2,
        "cover_letter": "Я готовий працювати над цим проектом!",
        "bid_amount": 1200,
        "status": "pending"
    }

    result = await proposals_collection.insert_one(new_proposal)
    print(f"Пропозиція додана з ID: {result.inserted_id}")


# Функція для вставки повідомлень
async def insert_message():
    db = await get_db()
    messages_collection = db["messages"]

    # Приклад повідомлення
    new_message = {
        "contract_id": 1,
        "sender_id": 1,
        "receiver_id": 2,
        "body": "Привіт! Як йде робота?",
        "sent_at": "2025-11-26T12:00:00Z",
        "is_read": False,
        "is_deleted": False
    }

    result = await messages_collection.insert_one(new_message)
    print(f"Повідомлення додано з ID: {result.inserted_id}")


# Асинхронно запускаємо функції
async def main():
    await insert_project()
    await insert_proposal()
    await insert_message()


asyncio.run(main())
