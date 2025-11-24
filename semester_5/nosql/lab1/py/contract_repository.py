# contract_repository.py

from typing import Any, Dict, List, Optional

from base_repository import BaseRepository


class ContractRepository(BaseRepository):
    """
    Repository for working with contracts, milestones and payments
    using stored procedures and views.
    """

    # ---------- Contracts ----------

    def get_freelancer_active_contracts(self, freelancer_id: int) -> List[Dict[str, Any]]:
        """
        Get active contracts for a freelancer using v_freelancer_active_contracts.
        """
        where = "WHERE freelancer_id = %s"
        return self._fetch_view("v_freelancer_active_contracts", where, [freelancer_id])

    def get_contract_details(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed info about contract using v_contract_details.
        """
        where = "WHERE contract_id = %s"
        return self._fetch_one_from_view("v_contract_details", where, [contract_id])

    # ---------- Milestones and payments ----------

    def create_milestone(
        self,
        contract_id: int,
        title: str,
        description: str,
        due_date: Optional[str],
        amount: float,
        created_by: int,
    ) -> None:
        """
        Create milestone using sp_create_milestone.
        due_date should be in ISO format 'YYYY-MM-DD' or None.
        """
        params = [
            contract_id,
            title,
            description,
            due_date,
            amount,
            created_by,
        ]
        self._execute_procedure("sp_create_milestone", params)

    def pay_milestone(
        self,
        milestone_id: int,
        payer_id: int,
        payment_method: str,
    ) -> None:
        """
        Pay milestone using sp_pay_milestone.
        """
        params = [
            milestone_id,
            payer_id,
            payment_method,
        ]
        self._execute_procedure("sp_pay_milestone", params)
