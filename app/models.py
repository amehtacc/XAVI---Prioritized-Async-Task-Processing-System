from sqlalchemy import Column, String, Integer, Enum, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payload = Column(JSON)
    priority = Column(Enum("HIGH", "MEDIUM", "LOW", name="priority_enum"))
    status = Column(Enum("PENDING", "PROCESSING", "SUCCESS", "FAILED", name="status_enum"), default="PENDING")
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)