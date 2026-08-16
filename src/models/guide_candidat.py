from src.db.interface.postgresql import Base
from src.models.page_document import PageDocumentMixin


class GuideCandidat(Base, PageDocumentMixin):
    __tablename__ = "guide_candidat"
