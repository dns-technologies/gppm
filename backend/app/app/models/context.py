from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .access import Access  # noqa: F401


class Context(Base):
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, unique=True, index=True, nullable=False)
    server = Column(String, nullable=False)
    port = Column(Integer, default=5432)
    role = Column(String, nullable=False)
    database = Column(String, default="template1")
    encoded_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    accesses = relationship("Access", back_populates="context", passive_deletes=True)
