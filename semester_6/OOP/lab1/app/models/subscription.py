from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Subscription:
    id: int | None
    user_id: int
    publication_id: int
    months: int
    total_amount: Decimal
    status: str = "created"
