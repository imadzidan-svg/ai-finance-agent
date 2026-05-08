from sqlalchemy import Column, Integer, Float, String, Text
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