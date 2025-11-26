# project_repository.py

from typing import Any, Dict, List, Optional

from .base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    """
    Repository for working with projects and proposals
    using stored procedures and views.
    """

    # ---------- Projects ----------

    def create_project(
        self,
        client_id: int,
        category_id: Optional[int],
        title: str,
        description: str,
        budget_min: Optional[float],
        budget_max: Optional[float],
        created_by: int,
    ) -> None:
        """
        Create new project using stored procedure sp_create_project.
        """
        params = [
            client_id,
            category_id,
            title,
            description,
            budget_min,
            budget_max,
            created_by,
        ]
        self._execute_procedure("sp_create_project", params)

    def soft_delete_project(self, project_id: int, user_id: int) -> None:
        """
        Soft delete project using sp_soft_delete_project.
        """
        self._execute_procedure("sp_soft_delete_project", [project_id, user_id])

    def restore_project(self, project_id: int, user_id: int) -> None:
        """
        Restore soft deleted project using sp_restore_project.
        """
        self._execute_procedure("sp_restore_project", [project_id, user_id])

    def get_open_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of open projects using view v_open_projects.
        """
        return self._fetch_view("v_open_projects")

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить проект по ID
        """
        sql = "SELECT * FROM projects WHERE project_id = %s"
        return self._fetch_one(sql, [project_id])

    # ---------- Proposals ----------

    def create_proposal(
        self,
        project_id: int,
        freelancer_id: int,
        cover_letter: str,
        bid_amount: float,
        created_by: int,
    ) -> None:
        """
        Create new proposal for a project using sp_create_proposal.
        """
        params = [
            project_id,
            freelancer_id,
            cover_letter,
            bid_amount,
            created_by,
        ]
        self._execute_procedure("sp_create_proposal", params)

    def accept_proposal(self, proposal_id: int, user_id: int) -> None:
        """
        Accept proposal and create contract using sp_accept_proposal.
        """
        self._execute_procedure("sp_accept_proposal", [proposal_id, user_id])
