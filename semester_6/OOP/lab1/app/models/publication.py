from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Publication:
    id: int | None
    title: str
    publisher: str
    period_months: int
    price: Decimal
