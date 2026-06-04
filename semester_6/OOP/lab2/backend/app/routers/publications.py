from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import User
from app.repositories import PublicationRepository
from app.schemas import PublicationCreate, PublicationRead, PublicationUpdate
from app.services import PublicationService

router = APIRouter(prefix="/api/publications", tags=["publications"])


def service(db: Session) -> PublicationService:
    return PublicationService(PublicationRepository(db))


@router.get("", response_model=list[PublicationRead])
def list_publications(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service(db).list_publications()


@router.post("", response_model=PublicationRead, status_code=status.HTTP_201_CREATED)
def create_publication(payload: PublicationCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return service(db).create(payload.title, payload.publisher, payload.period_months, payload.price)


@router.put("/{publication_id}", response_model=PublicationRead)
def update_publication(publication_id: int, payload: PublicationUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service(db).update(publication_id, payload.title, payload.publisher, payload.period_months, payload.price)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_publication(publication_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        service(db).delete(publication_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
