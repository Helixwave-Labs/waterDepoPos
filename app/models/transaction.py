import enum
from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, DateTime, Enum, Integer
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SaleType(str, enum.Enum):
    WHOLESALE = "wholesale"
    RETAIL = "retail"
    MIXED = "mixed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_type = Column(Enum(SaleType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("TransactionItem", back_populates="transaction")

class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)
    sale_type = Column(Enum(SaleType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=SaleType.RETAIL)

    transaction = relationship("Transaction", back_populates="items")