from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.transaction import SaleType

class TransactionItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class TransactionCreate(BaseModel):
    sale_type: SaleType
    items: List[TransactionItemCreate]

class TransactionItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_sale: float

class TransactionResponse(BaseModel):
    id: int
    total_amount: float
    sale_type: SaleType
    created_at: datetime
    items: List[TransactionItemResponse]