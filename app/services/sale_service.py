from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.transaction import Transaction, TransactionItem, SaleType
from app.models.product import Product
from app.models.user import User
from app.schemas.transaction import TransactionItemCreate

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

        # Iterate through items to calculate total and deduct stock
        for item_data in items:
            # Lock the product row to prevent race conditions
            product = db.query(Product).filter(Product.id == item_data.product_id).with_for_update().first()
            
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}. Available: {product.stock_quantity}")
            
            # Determine price based on the item's sale type (Single vs Pack)
            if item_data.sale_type == SaleType.WHOLESALE:
                price = product.wholesale_price
            else:
                price = product.retail_price
            
            item_total = price * item_data.quantity
            total_amount += item_total
            
            # Deduct stock
            product.stock_quantity -= item_data.quantity
            
            # Create transaction item record
            db_item = TransactionItem(
                product_id=product.id,
                quantity=item_data.quantity,
                price_at_sale=price,
                sale_type=item_data.sale_type
            )
            db_items.append(db_item)
            
        # Create the main transaction record
        transaction = Transaction(
            user_id=user.id,
            total_amount=total_amount,
            sale_type=sale_type,
            items=db_items
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction