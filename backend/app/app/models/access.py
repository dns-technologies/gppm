from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .context import Context  # noqa: F401


class Access(Base):
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    database = Column(String, index=True)
    db_schema = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    user = relationship("User", back_populates="accesses")
    context_id = Column(
        Integer, ForeignKey("context.id", ondelete="CASCADE"), nullable=True
    )
    context = relationship("Context", back_populates="accesses")
