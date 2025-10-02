from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.session import Base

class Sale(Base):
	__tablename__ = "sales"

	id = Column(Integer, primary_key=True, index=True)
	product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
	date = Column(Date, nullable=False, index=True)
	sales = Column(Integer, nullable=False)

	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	product = relationship("Product", backref="sales")