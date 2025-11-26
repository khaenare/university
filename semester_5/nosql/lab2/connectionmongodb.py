import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    # Підключення до MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    projects_collection = db["projects"]  # Оголошення колекції

    # Створення нового проекту
    new_project = {
        "title": "Розробка веб-сайту",
        "description": "Проект для створення корпоративного сайту",
        "budget": 5000
    }

    # Вставка документа в колекцію "projects"
    try:
        result = await projects_collection.insert_one(new_project)
        print("Проект успішно додано! ID:", result.inserted_id)
    except Exception as e:
        print(f"Помилка при додаванні проекту: {e}")

# Виконання асинхронної функції
asyncio.run(main())
