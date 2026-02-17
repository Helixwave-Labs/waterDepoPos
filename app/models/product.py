from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    wholesale_price = Column(Float, nullable=False)
    retail_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=2, nullable=False)
    is_active = Column(Boolean, default=True)
    sku = Column(String, unique=True, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    image = Column(String, nullable=True)  # Path or URL to image file