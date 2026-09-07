from sqlalchemy import Column, Integer, String, DateTime,Numeric,BigInteger, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.app.database import Base

class Resource(Base):
    __tablename__ = "resources"
    id=Column(Integer, primary_key=True, index=True)
    vm_name=Column(String(255),nullable=False,unique=True)
    resource_id=Column(String(500))
    location=Column(String(100))
    power_state=Column(String(50))
    vm_size=Column(String(100))
    environment=Column(String(100))
    owner=Column(String(100))
    project=Column(String(100))
    tags=Column(JSONB)
    last_synced_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class Metric(Base):
    __tablename__="vm_metrics"
    id=Column(Integer,primary_key=True,index=True)
    vm_name=Column(String(255),nullable=False)
    cpu_percent=Column(Numeric(5,2))
    network_in_bytes=Column(BigInteger)
    network_out_bytes=Column(BigInteger)
    recorded_at=Column(DateTime(timezone=True),server_default=func.now())

class Budget(Base):
    __tablename__="budgets"
    id=Column(Integer,primary_key=True,index=True)
    project=Column(String(100),nullable=False)
    monthly_limit=Column(Numeric(10,2),nullable=False)
    warning_threshold_percent=Column(Numeric(5,2),default=75.0)
    critical_threshold_percent=Column(Numeric(5,2),default=90.0)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class Alert(Base):
    __tablename__="alerts"
    id=Column(Integer, primary_key=True, index=True)
    alert_type=Column(String(50),nullable=False)
    vm_name=Column(String(255))
    budget_id=Column(Integer)
    severity=Column(String(20),nullable=False)
    message=Column(Text, nullable=False)
    acknowledged=Column(Boolean,default=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())