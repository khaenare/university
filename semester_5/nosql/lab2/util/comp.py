from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


async def fetch_projects_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    projects_collection = db["projects"]

    projects = await projects_collection.find().to_list(length=100)

    for project in projects:
        print(f"MongoDB Project: {project}")


asyncio.run(fetch_projects_mongo())

print(f"-----------------------------------------")

async def fetch_proposals_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    proposals_collection = db["proposals"]

    proposals = await proposals_collection.find().to_list(length=100)

    for proposal in proposals:
        print(f"MongoDB Proposal: {proposal}")


asyncio.run(fetch_proposals_mongo())

print(f"-----------------------------------------")
async def fetch_messages_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["freelance_platform"]
    messages_collection = db["messages"]

    messages = await messages_collection.find().to_list(length=100)

    for message in messages:
        print(f"MongoDB Message: {message}")


asyncio.run(fetch_messages_mongo())
print(f"-----------------------------------------")
print(f"*")
print(f"-----------------------------------------")
import psycopg2


def fetch_projects_sql():
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    for project in projects:
        print(f"SQL Project: {project}")

    cursor.close()
    conn.close()


fetch_projects_sql()

print(f"-----------------------------------------")

def fetch_proposals_sql():
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM proposals")
    proposals = cursor.fetchall()

    for proposal in proposals:
        print(f"SQL Proposal: {proposal}")

    cursor.close()
    conn.close()


fetch_proposals_sql()

print(f"-----------------------------------------")

def fetch_messages_sql():
    conn = psycopg2.connect(
        dbname="template1",
        user="matvii",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()

    for message in messages:
        print(f"SQL Message: {message}")

    cursor.close()
    conn.close()


fetch_messages_sql()


