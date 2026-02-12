import logging
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    db = SessionLocal()
    
    username = "admin"
    password = "adminpassword"
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role=UserRole.OWNER,
            is_active=True
        )
        db.add(user)
        db.commit()
        logger.info(f"Superuser {username} created")
    else:
        logger.info(f"Superuser {username} already exists")

if __name__ == "__main__":
    init_db()