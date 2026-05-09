from sqlalchemy import Column, Integer, Float, String, ForeignKey

from app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    upload_id = Column(Integer, ForeignKey("uploads.id"))

    description = Column(String)

    amount = Column(Float)

    type = Column(String)

    category = Column(String)