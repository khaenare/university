# message_repository.py

from typing import Any, List, Dict, Optional
from .base_repository import BaseRepository

class MessageRepository(BaseRepository):
    """
    Repository for working with messages using stored procedures and views.
    """

    def get_messages_by_contract(self, contract_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages related to a specific contract using the view `v_contract_messages`.
        """
        where = "WHERE contract_id = %s"
        return self._fetch_view("v_contract_messages", where, [contract_id])

    def create_message(
        self,
        contract_id: int,
        sender_id: int,
        receiver_id: int,
        body: str,
        is_read: bool,
        is_deleted: bool,
        sent_at: str,
    ) -> None:
        """
        Create a new message using sp_create_message.
        sent_at should be in ISO format 'YYYY-MM-DD HH:MM:SS' or None.
        """
        params = [
            contract_id,
            sender_id,
            receiver_id,
            body,
            is_read,
            is_deleted,
            sent_at,
        ]
        self._execute_procedure("sp_create_message", params)
