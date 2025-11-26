from lab1.py.unit_of_work import UnitOfWork





def insert_project():
    # Пример данных о проекте
    CLIENT_ID = 1
    CATEGORY_ID = 1  # Например, категория для проектов
    project_data = {
        "title": "Landing page for fintech startup",
        "description": "Need responsive landing page with modern design.",
        "budget_min": 500.0,
        "budget_max": 1000.0,
        "created_by": CLIENT_ID
    }

    # Вставка проекта с использованием UnitOfWork
    with UnitOfWork() as uow:
        uow.projects.create_project(
            client_id=CLIENT_ID,
            category_id=CATEGORY_ID,
            title=project_data["title"],
            description=project_data["description"],
            budget_min=project_data["budget_min"],
            budget_max=project_data["budget_max"],
            created_by=project_data["created_by"]
        )
        print("Project created via sp_create_project.")

insert_project()


def insert_proposal():
    PROJECT_ID = 1  # Например, ID проекта, на который фрилансер отправляет предложение
    FREELANCER_ID = 2  # ID фрилансера
    proposal_data = {
        "cover_letter": "I have strong experience in React and modern UI.",
        "bid_amount": 750.0,
        "created_by": FREELANCER_ID
    }

    # Вставка предложения с использованием UnitOfWork
    with UnitOfWork() as uow:
        uow.projects.create_proposal(
            project_id=PROJECT_ID,
            freelancer_id=FREELANCER_ID,
            cover_letter=proposal_data["cover_letter"],
            bid_amount=proposal_data["bid_amount"],
            created_by=proposal_data["created_by"]
        )
        print("Proposal created via sp_create_proposal.")

insert_proposal()

def insert_contract():
    PROJECT_ID = 1
    CLIENT_ID = 1
    FREELANCER_ID = 2
    contract_data = {
        "start_date": "2025-11-01",
        "status": "active",
        "hourly_rate": 20.0,
        "fixed_price": 1000.0,
        "created_by": CLIENT_ID
    }

    # Вставка контракта с использованием UnitOfWork
    with UnitOfWork() as uow:
        uow.contracts.create_contract(
            project_id=PROJECT_ID,
            client_id=CLIENT_ID,
            freelancer_id=FREELANCER_ID,
            start_date=contract_data["start_date"],
            status=contract_data["status"],
            hourly_rate=contract_data["hourly_rate"],
            fixed_price=contract_data["fixed_price"],
            created_by=contract_data["created_by"]
        )
        print("Contract created.")

# Сначала создаем контракт
insert_contract()


def insert_message():
    CONTRACT_ID = 1  # Предположим, что у нас уже есть контракт с ID 1
    SENDER_ID = 1    # ID отправителя (например, клиент)
    RECEIVER_ID = 2  # ID получателя (например, фрилансер)
    message_data = {
        "body": "Привіт! Як йде робота?",
        "is_read": False,
        "is_deleted": False,
        "sent_at": "2025-11-26T12:00:00Z"
    }

    # Вставка сообщения с использованием UnitOfWork
    with UnitOfWork() as uow:
        uow.messages.create_message(
            contract_id=CONTRACT_ID,
            sender_id=SENDER_ID,
            receiver_id=RECEIVER_ID,
            body=message_data["body"],
            is_read=message_data["is_read"],
            is_deleted=message_data["is_deleted"],
            sent_at=message_data["sent_at"]
        )
        print("Message created via sp_create_message.")

insert_message()