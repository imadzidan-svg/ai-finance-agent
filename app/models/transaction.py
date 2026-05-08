from sqlalchemy import Column, Integer, Float, String

from app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    description = Column(String)

    amount = Column(Float)

    type = Column(String)

    category = Column(String)