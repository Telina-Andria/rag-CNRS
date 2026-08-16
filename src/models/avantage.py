from src.db.interface.postgresql import Base
from src.models.page_document import PageDocumentMixin


class Avantage(Base, PageDocumentMixin):
    __tablename__ = "avantages"
