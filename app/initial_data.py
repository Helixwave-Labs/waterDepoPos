import logging

from sqlalchemy import text
from alembic import command
from alembic.config import Config
# Import your database session and models here
from app.db.session import SessionLocal
# Adjust the import path for User if it is located in app.models.user
from app.models.user import User, UserRole
# Assuming you have a security utility for hashing
from app.core.security import get_password_hash
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Check for missing data and add it if necessary.
    Also runs database migrations to ensure the schema matches the models.
    """
    # Migrations are now run manually, not on app startup

    db = SessionLocal()
    
    try:
        db.execute(text("SELECT 1"))
        logger.info("Successfully connected to the database")
        # Example: Check if admin exists, if not create
        user = db.query(User).filter(User.username == "admin@waterdepot.com").first()
        if not user:
            logger.info("Creating admin user...")
            user = User(
                username="admin@waterdepot.com",
                hashed_password=get_password_hash("admin"),
                role=UserRole.OWNER,
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