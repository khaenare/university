# base_repository.py

from typing import Any, Dict, List, Optional, Sequence


class BaseRepository:
    """
    Base repository with helper methods to work with stored procedures and views.
    All child repositories should use these helpers instead of raw SQL.
    """

    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def _execute_procedure(self, proc_name: str, params: Optional[Sequence[Any]] = None) -> None:
        """
        Execute stored procedure using CALL syntax.
        """
        if params:
            placeholders = ", ".join(["%s"] * len(params))
            sql = f"CALL {proc_name}({placeholders})"
        else:
            sql = f"CALL {proc_name}()"

        self.cursor.execute(sql, params or [])

    def _fetch_view(
        self,
        view_name: str,
        where_clause: str = "",
        params: Optional[Sequence[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Select data from a view and return list of dicts.
        where_clause should start with 'WHERE' if needed.
        """
        sql = f"SELECT * FROM {view_name} {where_clause}"
        self.cursor.execute(sql, params or [])

        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()

        result: List[Dict[str, Any]] = []
        for row in rows:
            item = {col: row[idx] for idx, col in enumerate(columns)}
            result.append(item)
        return result

    def _fetch_one_from_view(
        self,
        view_name: str,
        where_clause: str = "",
        params: Optional[Sequence[Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row from view or return None.
        """
        sql = f"SELECT * FROM {view_name} {where_clause} LIMIT 1"
        self.cursor.execute(sql, params or [])

        if self.cursor.rowcount == 0:
            return None

        columns = [desc[0] for desc in self.cursor.description]
        row = self.cursor.fetchone()
        return {col: row[idx] for idx, col in enumerate(columns)}
