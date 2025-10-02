from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db.session import Base

class Product(Base):
	__tablename__ = "products"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True, nullable=False)
	category = Column(String, nullable=True, index=True)
	price = Column(Float, nullable=True)
	stock = Column(Integer, nullable=True)

	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)