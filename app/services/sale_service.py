from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.transaction import Transaction, TransactionItem, SaleType
from app.models.user import User
from app.schemas.transaction import TransactionItemCreate
from typing import List

class SaleService:
    @staticmethod
    def process_sale(
        db: Session, 
        user: User, 
        items: List[TransactionItemCreate], 
        sale_type: SaleType
    ) -> Transaction:
        total_amount = 0.0
        db_items = []

        # We do not commit here immediately. We let the caller or the end of the request handle commit,
        # BUT for locking to work effectively in a transaction block, we usually need an active transaction.
        # FastAPI's dependency injection usually starts a transaction.
        
        for item in items:
            # LOCK the row for update to prevent race conditions
            stmt = select(Product).where(Product.id == item.product_id).with_for_update()
            product = db.execute(stmt).scalar_one_or_none()

            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            if product.stock_quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product: {product.name}")

            # Determine Price
            price = product.wholesale_price if sale_type == SaleType.WHOLESALE else product.retail_price
            
            # Deduct Stock
            product.stock_quantity -= item.quantity
            
            # Create Item Snapshot
            db_item = TransactionItem(
                product_id=product.id,
                quantity=item.quantity,
                price_at_sale=price
            )
            db_items.append(db_item)
            total_amount += (price * item.quantity)

        transaction = Transaction(user_id=user.id, total_amount=total_amount, sale_type=sale_type, items=db_items)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction