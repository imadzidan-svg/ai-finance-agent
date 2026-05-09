from sqlalchemy import Column, Integer, Float, String, Text,Boolean
from app.database import Base
from sqlalchemy.dialects.postgresql import JSON


class Upload(Base):

    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    total_income = Column(Float)

    total_expense = Column(Float)

    balance = Column(Float)

    ai_insights = Column(JSON)

    is_processed = Column(Boolean, default=False)

    processing_status = Column(String, default="pending")