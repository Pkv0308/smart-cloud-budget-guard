from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.app.database import Base

class Resource(Base):
    __tablename__ = "resources"
    id=Column(Integer, primary_key=True, index=True)
    vm_name=Column(String(255),nullable=False,unique=True)
    location=Column(String(100))
    power_state=Column(String(50))
    environment=Column(String(100))
    owner=Column(String(100))
    project=Column(String(100))
    tags=Column(JSONB)
    last_synced_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    