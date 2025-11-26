import time
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def insert_mongo_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    projects_collection = db["projects"]
    proposals_collection = db["proposals"]
    messages_collection = db["messages"]

    start_time = time.time()

    # Вставляємо 10000 проектів
    for i in range(100000):
        project = {
            "title": f"Project {i}",
            "description": "Project description",
            "budget": 5000,
            "status": "open"
        }
        await projects_collection.insert_one(project)

    # Вставляємо 10000 пропозицій
    for i in range(100000):
        proposal = {
            "project_id": i,
            "freelancer_id": 1,
            "cover_letter": "Cover letter",
            "bid_amount": 1000,
            "status": "pending"
        }
        await proposals_collection.insert_one(proposal)

    # Вставляємо 10000 повідомлень
    for i in range(100000):
        message = {
            "contract_id": i,
            "sender_id": 1,
            "receiver_id": 2,
            "body": "Message body",
            "sent_at": "2025-11-26T12:00:00Z",
            "is_read": False,
            "is_deleted": False
        }
        await messages_collection.insert_one(message)

    end_time = time.time()

    print(f"Час, витрачений на вставку 10,000 документів у MongoDB: {end_time - start_time} секунд")

asyncio.run(insert_mongo_data())

async def fetch_mongo_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    projects_collection = db["projects"]

    start_time = time.time()

    # Отримуємо всі проекти
    async for project in projects_collection.find():
        pass  # Просто читаємо всі проекти

    end_time = time.time()
    print(f"Час, витрачений на отримання всіх проектів з MongoDB: {end_time - start_time} секунд")

asyncio.run(fetch_mongo_data())
