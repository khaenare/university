from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Payment, Publication, Subscription, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_username(self, username: str) -> User | None:
        return self._db.scalar(select(User).where(User.username == username))

    def find_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)


class PublicationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self) -> list[Publication]:
        return list(self._db.scalars(select(Publication).order_by(Publication.title)).all())

    def find_by_id(self, publication_id: int) -> Publication | None:
        return self._db.get(Publication, publication_id)

    def create(self, publication: Publication) -> Publication:
        self._db.add(publication)
        self._db.commit()
        self._db.refresh(publication)
        return publication

    def update(self, publication: Publication) -> Publication:
        self._db.commit()
        self._db.refresh(publication)
        return publication

    def delete(self, publication: Publication) -> None:
        self._db.delete(publication)
        self._db.commit()


class SubscriptionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user: User) -> list[Subscription]:
        stmt = select(Subscription).options(selectinload(Subscription.publication)).order_by(Subscription.id)
        if not user.is_admin:
            stmt = stmt.where(Subscription.user_id == user.id)
        return list(self._db.scalars(stmt).all())

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        return self._db.scalar(
            select(Subscription)
            .options(selectinload(Subscription.publication))
            .where(Subscription.id == subscription_id)
        )

    def create(self, subscription: Subscription) -> Subscription:
        self._db.add(subscription)
        self._db.commit()
        self._db.refresh(subscription)
        self._db.refresh(subscription, ["publication"])
        return subscription

    def update(self, subscription: Subscription) -> Subscription:
        self._db.commit()
        self._db.refresh(subscription)
        self._db.refresh(subscription, ["publication"])
        return subscription

    def delete(self, subscription: Subscription) -> None:
        self._db.delete(subscription)
        self._db.commit()


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_subscription(self, subscription_id: int) -> list[Payment]:
        return list(self._db.scalars(select(Payment).where(Payment.subscription_id == subscription_id).order_by(Payment.id)).all())

    def find_by_id(self, payment_id: int) -> Payment | None:
        return self._db.get(Payment, payment_id)

    def create(self, payment: Payment) -> Payment:
        self._db.add(payment)
        self._db.commit()
        self._db.refresh(payment)
        return payment

    def update(self, payment: Payment) -> Payment:
        self._db.commit()
        self._db.refresh(payment)
        return payment

    def delete(self, payment: Payment) -> None:
        self._db.delete(payment)
        self._db.commit()
