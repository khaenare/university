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

    # Вставляем 10000 проектов
    for i in range(100000):
        project = {
            "title": f"Project {i}",
            "description": "Project description",
            "budget": 5000,
            "status": "open"
        }
        await projects_collection.insert_one(project)

    # Вставляем 10000 предложений
    for i in range(100000):
        proposal = {
            "project_id": i,
            "freelancer_id": 1,
            "cover_letter": "Cover letter",
            "bid_amount": 1000,
            "status": "pending"
        }
        await proposals_collection.insert_one(proposal)

    # Вставляем 10000 сообщений
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

    print(f"Time taken to insert 10,000 documents in MongoDB: {end_time - start_time} seconds")

asyncio.run(insert_mongo_data())

async def fetch_mongo_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    projects_collection = db["projects"]

    start_time = time.time()

    # Извлекаем все проекты
    async for project in projects_collection.find():
        pass  # Просто читаем все проекты

    end_time = time.time()
    print(f"Time taken to fetch all projects from MongoDB: {end_time - start_time} seconds")

asyncio.run(fetch_mongo_data())

