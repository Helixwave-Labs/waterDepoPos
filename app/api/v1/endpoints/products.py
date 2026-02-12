from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(Product).filter(Product.is_active == True)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=ProductResponse)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product