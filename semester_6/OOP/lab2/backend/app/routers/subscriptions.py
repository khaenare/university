from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.repositories import PaymentRepository, PublicationRepository, SubscriptionRepository
from app.schemas import PaymentCreate, PaymentRead, PaymentUpdate, SubscriptionCreate, SubscriptionRead, SubscriptionUpdate
from app.services import SubscriptionService

router = APIRouter(prefix="/api", tags=["subscriptions"])


def service(db: Session) -> SubscriptionService:
    return SubscriptionService(PublicationRepository(db), SubscriptionRepository(db), PaymentRepository(db))


def map_domain_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PermissionError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if "not found" in str(exc).lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/subscriptions", response_model=list[SubscriptionRead])
def list_subscriptions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service(db).list_for_user(user)


@router.post("/subscriptions", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(payload: SubscriptionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return service(db).subscribe(user, payload.publication_id, payload.months)
    except ValueError as exc:
        raise map_domain_error(exc)


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(subscription_id: int, payload: SubscriptionUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return service(db).update_subscription(subscription_id, payload.months, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service(db).delete_subscription(subscription_id, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)


@router.get("/subscriptions/{subscription_id}/payments", response_model=list[PaymentRead])
def list_payments(subscription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return service(db).list_payments(subscription_id, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)


@router.post("/subscriptions/{subscription_id}/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(subscription_id: int, payload: PaymentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return service(db).register_payment(subscription_id, payload.amount, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)


@router.put("/payments/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: int, payload: PaymentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return service(db).update_payment_status(payment_id, payload.status, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service(db).delete_payment(payment_id, user)
    except (ValueError, PermissionError) as exc:
        raise map_domain_error(exc)
