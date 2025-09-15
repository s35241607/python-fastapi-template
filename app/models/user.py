from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from app.config import settings

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": settings.schema}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    tickets = relationship("Ticket", back_populates="user")
    comments = relationship("Comment", back_populates="user")
