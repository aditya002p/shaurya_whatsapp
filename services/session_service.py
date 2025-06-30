import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.session import Session, Base
from models.agent import Agent
from config import Config

class SessionService:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_session(self, agent_id: int, agent_mobile: str) -> str:
        """
        Creates a new session for an agent and returns the session ID.
        The agent's mobile is used as the initial mobile number for the session.
        """
        session_id = str(uuid.uuid4())
        with self.Session() as db_session:
            new_session = Session(
                session_id=session_id,
                agent_id=agent_id,
                user_mobile=agent_mobile,
                current_state=Config.SESSION_STATES["INIT"]
            )
            db_session.add(new_session)
            db_session.commit()
            return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Gets the raw SQLAlchemy Session object."""
        with self.Session() as db_session:
            return db_session.query(Session).filter_by(session_id=session_id).first()

    def update_session(self, session_id: str, **kwargs) -> bool:
        """
        Updates a session with the given key-value pairs.
        """
        with self.Session() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if not session:
                return False
            
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            db_session.commit()
            return True

    def add_document_to_session(self, session_id: str, doc_type: str, doc_path: str) -> bool:
        """
        Adds a document path to the session's JSONB field.
        """
        with self.Session() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if not session:
                return False

            if session.documents is None:
                session.documents = {}
            
            session.documents[doc_type] = doc_path
            db_session.commit()
            return True
    
    def complete_session(self, session_id: str) -> bool:
        """
        Marks a session as completed and inactive.
        """
        return self.update_session(
            session_id, 
            is_active=False, 
            current_state=Config.SESSION_STATES["COMPLETED"]
        )

    def get_agent_info(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """
        Get agent information
        """
        with self.Session() as db_session:
            agent = db_session.query(Agent).filter(Agent.id == agent_id).first()
            
            if agent:
                return {
                    "id": agent.id,
                    "name": f"{agent.first_name} {agent.last_name}",
                    "phone_number": agent.mobile_number,
                    "wallet_balance": agent.wallet_balance,
                    "fastags_left": agent.fastags_left
                }
            return None
