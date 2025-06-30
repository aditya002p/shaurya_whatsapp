from typing import Dict, Any, Optional
import random
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models.agent import Agent, Base
from config import Config
from services.shauryapay_api import ShauryapayAPI

class AgentService:
    """
    Handles business logic related to agents. It uses the ShauryapayAPI for external
    data and a local database for session-specific data like OTPs.
    """
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.shauryapay_api = ShauryapayAPI()

    def verify_agent_by_mobile(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        response = self.shauryapay_api.get_agent_by_mobile(mobile_number)
        if response.get("status") == "success" and response.get("data"):
            return response["data"].get("agent_details")
        return None

    def get_agent_details(self, agent_id: int) -> Optional[Dict[str, Any]]:
        response = self.shauryapay_api.get_agent_by_id(agent_id)
        if response.get("status") == "success" and response.get("data"):
            data = response["data"]
            agent_details = data.get("agent_details", {})
            fastag_counts = data.get("fastag_status_counts", {})
            return {
                "id": int(agent_details.get("id", agent_id)),
                "first_name": agent_details.get("first_name"),
                "last_name": agent_details.get("last_name"),
                "mobile_number": agent_details.get("mobile_number"),
                "wallet_balance": float(data.get("wallet_balance", 0)),
                "fastags_left": int(fastag_counts.get("available", 0))
            }
        return None

    def generate_and_send_otp(self, agent_id: int, mobile_number: str) -> Optional[str]:
        otp = str(random.randint(1000, 9999))

        with self.Session() as session:
            agent = session.query(Agent).filter_by(mobile_number=mobile_number).first()

            if agent:
                # Update existing agent's OTP
                agent.otp = otp
                agent.otp_created_at = datetime.utcnow()
                session.commit()
                print(f"Debug: Updated OTP for existing agent. Agent ID: {agent.id}, OTP: {otp}")
            else:
                # Try to find agent by ID
                agent = session.query(Agent).filter_by(id=agent_id).first()
                if not agent:
                    # Get agent details from ShauryaPay API
                    agent_details = self.shauryapay_api.get_agent_by_id(agent_id)
                    if not agent_details or not agent_details.get("data"):
                        return None

                    agent_data = agent_details["data"]
                    agent = Agent(
                        id=agent_id,
                        mobile_number=mobile_number,
                        first_name=agent_data.get("first_name", "Agent"),
                        last_name=agent_data.get("last_name", str(agent_id)),
                        wallet_balance=agent_data.get("wallet_balance", 0),
                        fastags_left=agent_data.get("fastags_left", 0),
                        otp=otp,
                        otp_created_at=datetime.utcnow()
                    )
                    session.add(agent)
                    print(f"Debug: Created new agent with OTP. Agent ID: {agent_id}, OTP: {otp}")
                else:
                    # Update mobile number and OTP of existing agent
                    agent.mobile_number = mobile_number
                    agent.otp = otp
                    agent.otp_created_at = datetime.utcnow()
                    print(f"Debug: Updated OTP for agent by ID. Agent ID: {agent.id}, OTP: {otp}")
                session.commit()

        # Send OTP via SMS using bhashsms.com API
        message = f"Dear Partner, use OTP {otp} for login at agent app - ShauryaPay"
        params = {
            "user": Config.SMS_USER,
            "pass": Config.SMS_PASS,
            "sender": Config.SMS_SENDER,
            "phone": mobile_number,
            "text": message,
            "priority": Config.SMS_PRIORITY,
            "stype": Config.SMS_STYPE
        }

        try:
            response = requests.get(Config.SMS_URL, params=params, timeout=10)
            response.raise_for_status()
            print(f"Debug: SMS sent successfully. Response: {response.text}")
            return otp
        except requests.exceptions.RequestException as e:
            print(f"Debug: SMS sending failed. Error: {str(e)}")
            if Config.DEBUG:
                return otp
            return None

    def get_agent_details_by_mobile(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        response = self.shauryapay_api.get_agent_by_mobile(mobile_number)
        if response.get("status") == "success" and response.get("data"):
            data = response["data"]
            agent_details = data.get("agent_details", {})
            fastag_counts = data.get("fastag_status_counts", {})
            return {
                "id": int(agent_details.get("id")),
                "first_name": agent_details.get("first_name"),
                "last_name": agent_details.get("last_name"),
                "mobile_number": agent_details.get("mobile_number"),
                "wallet_balance": float(data.get("wallet_balance", 0)),
                "fastags_left": int(fastag_counts.get("available", 0))
            }
        return None

    def verify_otp(self, mobile_number: str, otp: str) -> bool:
        with self.Session() as session:
            agent = session.query(Agent).filter_by(mobile_number=mobile_number).first()
            print(f"Debug: Verifying OTP. Mobile: {mobile_number}, Provided OTP: {otp}")

            if not agent:
                print(f"Debug: Agent not found with mobile: {mobile_number}")
                return False

            stored_otp = agent.otp
            print(f"Debug: Stored OTP: {stored_otp}")

            if not stored_otp:
                print("Debug: No OTP stored for agent")
                return False

            is_valid = str(stored_otp) == str(otp)
            print(f"Debug: OTP comparison result: {is_valid}")

            if is_valid:
                agent.otp = None
                agent.otp_created_at = None
                session.commit()
                print("Debug: OTP verified and cleared")

            return is_valid
