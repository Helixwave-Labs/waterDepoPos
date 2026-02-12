from typing import Optional
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str
    wholesale_price: float = Field(..., gt=0)
    retail_price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    low_stock_threshold: int = 2
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True