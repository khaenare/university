from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.database import Base


class RoleMixin:
    role: Mapped[str]

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class User(RoleMixin, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'reader')", name="ck_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Publication(Base):
    __tablename__ = "publications"
    __table_args__ = (
        CheckConstraint("period_months > 0", name="ck_publications_period_positive"),
        CheckConstraint("price >= 0", name="ck_publications_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    period_months: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="publication", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("months > 0", name="ck_subscriptions_months_positive"),
        CheckConstraint("total_amount >= 0", name="ck_subscriptions_total_non_negative"),
        CheckConstraint("status IN ('created', 'active', 'cancelled')", name="ck_subscriptions_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    months: Mapped[int] = mapped_column(nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="created")
    created_at = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="subscriptions")
    publication: Mapped[Publication] = relationship(back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
        CheckConstraint("status IN ('registered', 'paid', 'cancelled')", name="ck_payments_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="registered")
    created_at = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    subscription: Mapped[Subscription] = relationship(back_populates="payments")
