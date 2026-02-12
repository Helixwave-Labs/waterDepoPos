from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.v1 import deps
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
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
    return SaleService.process_sale(
        db=db,
        user=current_user,
        items=transaction_in.items,
        sale_type=transaction_in.sale_type
    )

@router.get("/stats")
def get_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    total_sales = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
    count = db.query(Transaction).count()
    return {"total_revenue": total_sales, "transaction_count": count}