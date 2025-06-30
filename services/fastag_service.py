from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.fastag import Fastag, Base
from config import Config

class FastagService:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create(self, session_id, agent_id, vehicle_number, barcode, serial_number, customer_name, customer_mobile, plan):
        db = self.Session()
        f = Fastag(
            session_id=session_id,
            agent_id=agent_id,
            vehicle_number=vehicle_number,
            barcode=barcode,
            serial_number=serial_number,
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            plan=plan,
            status="pending"
        )
        db.add(f)
        db.commit()
        db.close()
        return True 