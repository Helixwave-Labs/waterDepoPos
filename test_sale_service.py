import pytest
import threading
from app.services.sale_service import SaleService
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.transaction import SaleType
from app.schemas.transaction import TransactionItemCreate
from app.core.security import get_password_hash

def create_test_user(db):
    user = db.query(User).filter_by(username="test_staff").first()
    if not user:
        user = User(
            username="test_staff",
            hashed_password=get_password_hash("password"),
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def create_test_product(db, stock=10):
    product = Product(
        name="Test Water",
        wholesale_price=10.0,
        retail_price=15.0,
        stock_quantity=stock,
        low_stock_threshold=2
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def test_process_sale_deducts_stock(db):
    user = create_test_user(db)
    product = create_test_product(db, stock=20)
    
    items = [TransactionItemCreate(product_id=product.id, quantity=5)]
    
    # Process Sale
    transaction = SaleService.process_sale(db, user, items, SaleType.RETAIL)
    
    # Verify Transaction
    assert transaction.total_amount == 15.0 * 5
    assert transaction.sale_type == SaleType.RETAIL
    
    # Verify Stock Deduction
    db.refresh(product)
    assert product.stock_quantity == 15

def test_process_sale_concurrency_locking(db):
    """
    Verify that concurrent sales do not cause race conditions (lost updates).
    We will attempt to sell 1 item, 10 times concurrently.
    Starting stock is 10. Ending stock should be 0.
    Without locking, ending stock might be > 0.
    """
    user = create_test_user(db)
    product = create_test_product(db, stock=10)
    product_id = product.id
    
    def sell_item():
        # Each thread needs its own session
        from app.db.session import SessionLocal
        thread_db = SessionLocal()
        try:
            items = [TransactionItemCreate(product_id=product_id, quantity=1)]
            SaleService.process_sale(thread_db, user, items, SaleType.RETAIL)
        except Exception:
            pass # Ignore errors (like out of stock if we went over)
        finally:
            thread_db.close()

    threads = []
    for _ in range(10):
        t = threading.Thread(target=sell_item)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    db.refresh(product)
    assert product.stock_quantity == 0