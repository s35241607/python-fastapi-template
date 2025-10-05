from sqlalchemy import BigInteger, Column, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr

Base = declarative_base()

class Auditable:
    """Mixin for auditable models."""
    @declared_attr
    def created_by(cls):
        return Column(BigInteger)

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now())

    @declared_attr
    def updated_by(cls):
        return Column(BigInteger)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), onupdate=func.now())