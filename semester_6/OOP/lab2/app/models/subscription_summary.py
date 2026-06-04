from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SubscriptionSummary:
    id: int
    user_id: int
    publication_id: int
    publication_title: str
    months: int
    total_amount: Decimal
    status: str
