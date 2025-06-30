from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Fastag(Base):
    __tablename__ = "fastags"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    agent_id = Column(Integer, nullable=False)
    vehicle_number = Column(String, nullable=False)
    barcode = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_mobile = Column(String, nullable=True)
    plan = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="fastags")
    agent = relationship("Agent", back_populates="fastags")
    
    def __repr__(self):
        return f"<Fastag(id={self.id}, tag_number='{self.tag_number}')>"
