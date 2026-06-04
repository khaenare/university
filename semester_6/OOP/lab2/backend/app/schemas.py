from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class PublicationBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    publisher: str = Field(min_length=1, max_length=200)
    period_months: int = Field(gt=0)
    price: Decimal = Field(ge=0)


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(PublicationBase):
    pass


class PublicationRead(PublicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SubscriptionCreate(BaseModel):
    publication_id: int
    months: int = Field(gt=0)


class SubscriptionUpdate(BaseModel):
    months: int = Field(gt=0)


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    publication_id: int
    months: int
    total_amount: Decimal
    status: str
    created_at: datetime
    publication: PublicationRead


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)


class PaymentUpdate(BaseModel):
    status: str


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subscription_id: int
    amount: Decimal
    status: str
    created_at: datetime
