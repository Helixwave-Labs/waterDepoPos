from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
import os
from uuid import uuid4
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.services.storage_service import StorageService

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(Product).filter(Product.is_active == True)
    if search:
        # Search by name or SKU
        query = query.filter((Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%")))
    if category and category != "All":
        query = query.filter(Product.category == category)
        
    products = query.offset(skip).limit(limit).all()
    return [ProductResponse(
        id=str(p.id),
        name=p.name,
        sku=p.sku,
        category=p.category,
        wholesale_price=p.wholesale_price,
        retail_price=p.retail_price,
        stock_quantity=p.stock_quantity,
        low_stock_threshold=p.low_stock_threshold,
        is_active=p.is_active,
        image_url=p.image_url,
        created_at=p.created_at
    ) for p in products]

@router.post("/", response_model=ProductResponse)
async def create_product(
    db: Session = Depends(deps.get_db),
    name: str = Form(...),
    sku: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    wholesale_price: float = Form(...),
    retail_price: float = Form(...),
    stock_quantity: int = Form(...),
    low_stock_threshold: int = Form(2),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "owner": # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(status_code=403, detail="Not enough permissions")

    image_url = None
    if image:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG images are allowed.")

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid4().hex}{ext}"
        storage_service = StorageService()
        image_url = storage_service.upload_image(image, filename)

    product = Product(
        name=name,
        sku=sku,
        category=category,
        wholesale_price=wholesale_price,
        retail_price=retail_price,
        stock_quantity=stock_quantity,
        low_stock_threshold=low_stock_threshold,
        is_active=is_active,
        image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(
        id=str(product.id),
        name=product.name,
        sku=product.sku,
        category=product.category,
        wholesale_price=product.wholesale_price,
        retail_price=product.retail_price,
        stock_quantity=product.stock_quantity,
        low_stock_threshold=product.low_stock_threshold,
        is_active=product.is_active,
        image_url=product.image_url,
        created_at=product.created_at
    )

@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: str,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "owner": # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(status_code=403, detail="Not enough permissions")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.image_url:
        storage_service = StorageService()
        storage_service.delete_image(product.image_url)

    db.delete(product)
    db.commit()
    return ProductResponse(
        id=str(product.id),
        name=product.name,
        sku=product.sku,
        category=product.category,
        wholesale_price=product.wholesale_price,
        retail_price=product.retail_price,
        stock_quantity=product.stock_quantity,
        low_stock_threshold=product.low_stock_threshold,
        is_active=product.is_active,
        image_url=product.image_url,
        created_at=product.created_at
    )