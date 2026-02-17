import enum
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    OWNER = "owner"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.STAFF, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)