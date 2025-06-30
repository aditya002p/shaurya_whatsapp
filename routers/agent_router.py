from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.agent_service import AgentService
from services.session_service import SessionService
from utils.validators import Validators

# --- Router and Service Initialization ---
router = APIRouter(prefix="/agents", tags=["Agent Authentication"])
agent_service = AgentService()
session_service = SessionService()

# --- Pydantic Models ---
class MobileVerificationRequest(BaseModel):
    mobile_number: str

class OtpVerificationRequest(BaseModel):
    mobile_number: str
    otp: str

# --- API Endpoints ---
@router.post("/verify-mobile", summary="Verify Agent Mobile and Send OTP")
def verify_mobile_and_send_otp(request: MobileVerificationRequest):
    """
    1. Validates the mobile number format.
    2. Checks if the agent exists via an external API call.
    3. If the agent exists, generates and sends a 4-digit OTP.
    """
    if not Validators.validate_mobile(request.mobile_number):
        raise HTTPException(status_code=400, detail="Invalid mobile number format.")

    agent = agent_service.verify_agent_by_mobile(request.mobile_number)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found. Please use a registered mobile number.")

    agent_id = int(agent["id"])
    otp = agent_service.generate_and_send_otp(agent_id, request.mobile_number)
    if not otp:
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again later.")

    return {
        "message": "OTP sent successfully.",
        "agent_id": agent_id
    }

@router.post("/verify-otp", summary="Verify OTP and Get Agent Details")
def verify_otp_and_get_details(request: OtpVerificationRequest):
    """
    1. Verifies the provided OTP for the agent.
    2. If verification is successful, creates a new session.
    3. Fetches and returns the agent's full details, including wallet balance and FASTag count.
    """
    if not agent_service.verify_otp(request.mobile_number, request.otp):
        raise HTTPException(status_code=401, detail="Invalid OTP. Please try again.")

    agent_details = agent_service.get_agent_details_by_mobile(request.mobile_number)
    if not agent_details:
        raise HTTPException(status_code=404, detail="Could not retrieve agent details after OTP verification.")

    session_id = session_service.create_session(
        agent_id=agent_details["id"], 
        agent_mobile=agent_details["mobile_number"]
    )

    return {
        "message": f"Hi {agent_details['first_name']} 👋",
        "session_id": session_id,
        "agent_id": agent_details["id"],
        "agent_name": f"{agent_details['first_name']} {agent_details['last_name']}",
        "wallet_balance": agent_details["wallet_balance"],
        "fastags_left": agent_details["fastags_left"]
    }
