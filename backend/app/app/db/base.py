# flake8: noqa
# Импортируем все классы перед импортом их Alembic
from app.db.base_class import Base
from app.models.user import User
from app.models.access import Access
from app.models.context import Context
