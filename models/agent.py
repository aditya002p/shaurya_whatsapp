from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile_number = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    status = Column(String, default="1")
    distributor_id = Column(String, nullable=True)
    payout_details = Column(String, nullable=True)
    distributor_name = Column(String, nullable=True)
    wallet_balance = Column(Integer, default=0)
    fastags_left = Column(Integer, default=0)
    otp = Column(String, nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.first_name} {self.last_name}', phone='{self.mobile_number}')>"
