from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    vehicle_number = Column(String, nullable=False, unique=True)
    engine_number = Column(String, nullable=True)
    chassis_number = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    barcode = Column(String, nullable=True)
    
    # Vehicle details
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    descriptor = Column(String, nullable=True)  # Petrol, Diesel, CNG, etc.
    color = Column(String, nullable=True)
    type = Column(String, nullable=True)  # 4W, 2W, etc.
    vehicle_type = Column(String, nullable=True)  # LMV, HMV, etc.
    state_of_registration = Column(String, nullable=True)
    
    # Document paths
    rc_front_path = Column(String, nullable=True)
    rc_back_path = Column(String, nullable=True)
    vehicle_front_path = Column(String, nullable=True)
    vehicle_side_path = Column(String, nullable=True)
    tag_fixed_path = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="vehicles")
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, number='{self.vehicle_number}')>"
