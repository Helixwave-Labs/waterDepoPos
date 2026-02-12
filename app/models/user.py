import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    OWNER = "owner"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)