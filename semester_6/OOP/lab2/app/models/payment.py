from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Payment:
    id: int | None
    subscription_id: int
    amount: Decimal
    status: str = "registered"
