from decimal import Decimal

from app.database import SessionLocal
from app.models import Payment, Publication, Subscription, User
from app.security import hash_password


def seed() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username="admin").first():
            password_hash = hash_password("password")
            db.add_all([
                User(username="admin", password_hash=password_hash, role="admin"),
                User(username="reader", password_hash=password_hash, role="reader"),
                User(username="olena", password_hash=password_hash, role="reader"),
            ])
        if not db.query(Publication).first():
            db.add_all([
                Publication(title="Наука і життя", publisher="Українська преса", period_months=1, price=Decimal("120.00")),
                Publication(title="Бізнес тиждень", publisher="Media Group", period_months=1, price=Decimal("95.50")),
                Publication(title="Технології майбутнього", publisher="Digital Press", period_months=1, price=Decimal("149.00")),
            ])
        db.commit()
        reader = db.query(User).filter_by(username="reader").first()
        publication = db.query(Publication).filter_by(title="Наука і життя").first()
        if reader and publication and not db.query(Subscription).first():
            subscription = Subscription(user_id=reader.id, publication_id=publication.id, months=6, total_amount=publication.price * 6)
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            db.add(Payment(subscription_id=subscription.id, amount=subscription.total_amount))
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
