from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    wholesale_price: float = Field(..., gt=0)
    retail_price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    low_stock_threshold: int = 2
    is_active: bool = True
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True