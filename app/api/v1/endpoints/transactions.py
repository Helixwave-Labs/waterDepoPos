from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.v1 import deps
from app.models.user import User
from app.models.transaction import Transaction, TransactionItem
from app.models.product import Product
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionItemResponse, TopProduct
from app.services.sale_service import SaleService

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Both staff and owner can create transactions
    transaction = SaleService.process_sale(
        db=db,
        user=current_user,
        items=transaction_in.items,
        sale_type=transaction_in.sale_type
    )
    
    return TransactionResponse(
        id=str(transaction.id),
        total_amount=transaction.total_amount,
        sale_type=transaction.sale_type,
        created_at=transaction.created_at,
        items=[
            TransactionItemResponse(
                product_id=str(item.product_id),
                quantity=item.quantity,
                price_at_sale=item.price_at_sale,
                sale_type=item.sale_type
            ) for item in transaction.items
        ]
    )

@router.get("/stats")
def get_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Compare value, not SQLAlchemy column object
    if getattr(current_user, "role", None) != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    total_sales = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
    count = db.query(Transaction).count()
    
    # Get top selling products
    top_products_query = db.query(
        TransactionItem.product_id,
        Product.name,
        func.sum(TransactionItem.quantity).label("total_quantity")
    ).join(Product, TransactionItem.product_id == Product.id)\
     .group_by(TransactionItem.product_id, Product.name)\
     .order_by(func.sum(TransactionItem.quantity).desc())\
     .limit(5).all()

    # Convert UUID to string explicitly to avoid Pydantic validation error
    top_products = [TopProduct(product_id=str(row.product_id), name=row.name, quantity=row.total_quantity) for row in top_products_query]

    return {"total_revenue": total_sales, "transaction_count": count, "top_products": top_products}