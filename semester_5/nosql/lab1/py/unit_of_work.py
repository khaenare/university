# unit_of_work.py

from typing import Optional, Callable

from connection import get_connection
from project_repository import ProjectRepository
from contract_repository import ContractRepository


class UnitOfWork:
    """
    Unit of Work implementation for PostgreSQL.

    Usage:

        from unit_of_work import UnitOfWork

        with UnitOfWork() as uow:
            uow.projects.create_project(...)
            uow.contracts.get_contract_details(...)
    """

    def __init__(self, connection_factory: Callable = get_connection):
        self._connection_factory = connection_factory
        self.connection = None
        self.cursor = None

        # Repositories
        self.projects: Optional[ProjectRepository] = None
        self.contracts: Optional[ContractRepository] = None

    def __enter__(self):
        self.connection = self._connection_factory()
        self.cursor = self.connection.cursor()

        # Initialize repositories with shared connection and cursor
        self.projects = ProjectRepository(self.connection, self.cursor)
        self.contracts = ContractRepository(self.connection, self.cursor)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None:
                self.connection.close()

    def commit(self):
        """
        Explicit commit if needed.
        """
        if self.connection is not None:
            self.connection.commit()

    def rollback(self):
        """
        Explicit rollback if needed.
        """
        if self.connection is not None:
            self.connection.rollback()
