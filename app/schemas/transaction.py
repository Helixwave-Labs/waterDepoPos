from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.transaction import SaleType

class TransactionItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    sale_type: SaleType = SaleType.RETAIL

class TransactionCreate(BaseModel):
    sale_type: SaleType = SaleType.MIXED
    items: List[TransactionItemCreate]

class TransactionItemResponse(BaseModel):
    product_id: str
    quantity: int
    price_at_sale: float
    sale_type: SaleType

class TransactionResponse(BaseModel):
    id: str
    total_amount: float
    sale_type: SaleType
    created_at: datetime
    items: List[TransactionItemResponse]

class TopProduct(BaseModel):
    product_id: str
    name: str
    quantity: int