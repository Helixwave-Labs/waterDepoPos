from sqlalchemy.orm import Session
from app.models.product import Product

class InventoryService:
    @staticmethod
    def check_low_stock(db: Session, product_id: int) -> bool:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product and product.stock_quantity <= product.low_stock_threshold:
            return True
        return False