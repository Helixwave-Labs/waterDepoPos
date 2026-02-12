from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    wholesale_price = Column(Float, nullable=False)
    retail_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=2, nullable=False)
    is_active = Column(Boolean, default=True)