# main.py

from unit_of_work import UnitOfWork


def print_header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    # Example IDs; they must exist in the database:
    # - CLIENT_ID: user with user_type = 'client'
    # - FREELANCER_ID: user with user_type = 'freelancer'
    # - CATEGORY_ID: existing project category
    CLIENT_ID = 1
    FREELANCER_ID = 2
    CATEGORY_ID = 1

    with UnitOfWork() as uow:
        # 1. Create new project
        print_header("1. Creating new project")
        uow.projects.create_project(
            client_id=CLIENT_ID,
            category_id=CATEGORY_ID,
            title="Landing page for fintech startup",
            description="Need responsive landing page with modern design.",
            budget_min=500.0,
            budget_max=1000.0,
            created_by=CLIENT_ID,
        )
        print("Project created via sp_create_project.")

        # 2. Show open projects
        print_header("2. Open projects (v_open_projects)")
        open_projects = uow.projects.get_open_projects()
        for p in open_projects:
            print(f"- #{p['project_id']}: {p['title']} (client: {p['client_name']})")

        # For demo purposes we will take first project id
        if not open_projects:
            print("No open projects found. Demo will stop here.")
            return

        project_id = open_projects[0]["project_id"]

        # 3. Create proposal from freelancer
        print_header("3. Creating proposal for project")
        uow.projects.create_proposal(
            project_id=project_id,
            freelancer_id=FREELANCER_ID,
            cover_letter="I have strong experience in React and modern UI.",
            bid_amount=750.0,
            created_by=FREELANCER_ID,
        )
        print("Proposal created via sp_create_proposal.")

        # For simplicity we assume proposal_id = 1 or we can query it,
        # but lab focuses on procedures and views, so we keep it simple.
        PROPOSAL_ID = 1

        # 4. Client accepts proposal -> contract is created
        print_header("4. Accepting proposal and creating contract")
        uow.projects.accept_proposal(
            proposal_id=PROPOSAL_ID,
            user_id=CLIENT_ID,
        )
        print("Proposal accepted via sp_accept_proposal; contract should be created.")

        # 5. Show active contracts for freelancer
        print_header("5. Active contracts for freelancer (v_freelancer_active_contracts)")
        active_contracts = uow.contracts.get_freelancer_active_contracts(FREELANCER_ID)
        for c in active_contracts:
            print(
                f"- Contract #{c['contract_id']} for project #{c['project_id']}, "
                f"total_amount={c['total_amount']}"
            )

        if not active_contracts:
            print("No active contracts found. Demo will stop here.")
            return

        contract_id = active_contracts[0]["contract_id"]

        # 6. Create and pay milestone
        print_header("6. Creating and paying milestone")
        uow.contracts.create_milestone(
            contract_id=contract_id,
            title="Initial design",
            description="Wireframes and visual concept",
            due_date="2025-01-10",
            amount=300.0,
            created_by=CLIENT_ID,
        )
        print("Milestone created via sp_create_milestone.")

        # Again, for simplicity we assume milestone_id = 1
        MILESTONE_ID = 1

        uow.contracts.pay_milestone(
            milestone_id=MILESTONE_ID,
            payer_id=CLIENT_ID,
            payment_method="card",
        )
        print("Milestone paid via sp_pay_milestone.")

        # 7. Show contract details
        print_header("7. Contract details (v_contract_details)")
        details = uow.contracts.get_contract_details(contract_id)
        if details:
            print(f"Contract #{details['contract_id']}:")
            print(f"  Project: {details['project_title']}")
            print(f"  Client: {details['client_name']}")
            print(f"  Freelancer: {details['freelancer_name']}")
            print(f"  Total amount: {details['total_amount']}")
            print(f"  Freelancer rating: {details['freelancer_rating']}")
        else:
            print("No details found for contract.")


if __name__ == "__main__":
    main()
