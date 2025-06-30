from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_json import mutable_json_type
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    agent_id = Column(Integer, nullable=False)
    user_mobile = Column(String, nullable=True)
    current_state = Column(String, nullable=False, default="INIT")
    
    # User data
    vehicle_number = Column(String, nullable=True)
    engine_number = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    id_proof_type = Column(String, nullable=True)
    id_proof_number = Column(String, nullable=True)
    plan_selected = Column(String, nullable=True)
    
    # OTP and request data
    request_id = Column(String, nullable=True)
    shauryapay_session_id = Column(String, nullable=True)  # Session ID from Shauryapay API
    replace_user_mobile = Column(String, nullable=True)
    replace_request_id = Column(String, nullable=True)
    
    # Vehicle data
    serial_number = Column(String, nullable=True)
    barcode_selected = Column(String, nullable=True)
    vehicle_maker = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_descriptor = Column(String, nullable=True)
    
    # Document uploads
    documents = Column(mutable_json_type(dbtype=JSON), default=dict)
    
    # Session metadata
    is_active = Column(Integer, default=1)  # 1 for active, 0 for completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Session(id={self.id}, session_id='{self.session_id}', state='{self.current_state}')>"
