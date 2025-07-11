from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship

from app.backend.db import Base

from datetime import datetime, timedelta, timezone


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    comment = Column(String)
    comment_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    grade = Column(Float)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="review", uselist=False)
    product = relationship("Product", back_populates="reviews", uselist=False)
