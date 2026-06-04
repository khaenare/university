from decimal import Decimal

from app.models.publication import Publication


class PublicationService:
    def __init__(self, publication_dao) -> None:
        self._publication_dao = publication_dao

    def list_publications(self) -> list[Publication]:
        return self._publication_dao.list_all()

    def create(self, title: str, publisher: str, period_months: str, price: str) -> int:
        publication = Publication(None, title.strip(), publisher.strip(), int(period_months), Decimal(price))
        return self._publication_dao.create(publication)

    def update(self, publication_id: str, title: str, publisher: str, period_months: str, price: str) -> None:
        publication = Publication(int(publication_id), title.strip(), publisher.strip(), int(period_months), Decimal(price))
        self._publication_dao.update(publication)

    def delete(self, publication_id: str) -> None:
        self._publication_dao.delete(int(publication_id))
