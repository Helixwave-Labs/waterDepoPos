import logging

# Import your database session and models here
from app.db.session import SessionLocal
# Adjust the import path for User if it is located in app.models.user
from app.models.user import User
# Assuming you have a security utility for hashing
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Check for missing data and add it if necessary.
    """
    db = SessionLocal()
    
    try:
        # Example: Check if admin exists, if not create
        user = db.query(User).filter(User.email == "admin@waterdepot.com").first()
        if not user:
            logger.info("Creating admin user...")
            user = User(
                email="admin@waterdepot.com",
                hashed_password=get_password_hash("admin"),
                is_active=True,
                is_superuser=True,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()
    
    logger.info("Initial data check completed.")

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")