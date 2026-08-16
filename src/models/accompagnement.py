from src.db.interface.postgresql import Base
from src.models.page_document import PageDocumentMixin


class Accompagnement(Base, PageDocumentMixin):
    __tablename__ = "accompagnement"
