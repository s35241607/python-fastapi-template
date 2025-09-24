"""Shared dependency helpers.

This project uses class-based DI for repositories and services. Instead of
writing small factory functions like ``get_category_service`` we rely on
``Depends(MyClass)`` where ``MyClass``'s __init__ receives other dependencies.

Keep this module for other cross-cutting dependency factories.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


# Example helper if an explicit session factory is needed elsewhere:
# def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
#     return db
