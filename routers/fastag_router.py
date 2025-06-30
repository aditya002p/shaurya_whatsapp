from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from services.session_service import SessionService
from services.shauryapay_api import ShauryapayAPI
from services.agent_service import AgentService
from models.session import Session
from utils.validators import Validators

# --- Router and Service Initialization ---
router = APIRouter(prefix="/fastags", tags=["FASTag Issuance and Replacement"])
session_service = SessionService()
shauryapay_api = ShauryapayAPI()
agent_service = AgentService()

# --- Pydantic Models ---
class SessionRequest(BaseModel):
    session_id: str

class VehicleDetailsRequest(SessionRequest):
    vehicle_number: str
    engine_number: str  # Last 5 digits

class UserMobileRequest(SessionRequest):
    user_mobile: str

class UserOTPRequest(SessionRequest):
    otp: str

class UserInfoRequest(SessionRequest):
    first_name: str
    last_name: str
    dob: str  # DD-MM-YYYY

class IdProofRequest(SessionRequest):
    id_type: str  # 1: PAN, 2: Passport, 3: DL, 4: Voter ID
    id_number: str
    expiry_date: Optional[str] = None

class PlanRequest(SessionRequest):
    plan_id: str

class BarcodeRequest(SessionRequest):
    barcode: str

class VehicleInfoRequest(SessionRequest):
    maker: str
    model: str
    descriptor: str

class ConfirmationRequest(SessionRequest):
    confirm: bool

# --- Message Templates ---
class Message:
    VEHICLE_PROMPT = "Let's get your FASTag in just a few steps. 🚗 Please enter your Vehicle Number (e.g., MH12AB1234)."
    ENGINE_PROMPT = "Got it ✅ Share the last 5 digits of your engine number."
    USER_MOBILE_PROMPT = "Now, please send the user's 10-digit Mobile Number."
    OTP_PROMPT = "Sending OTP to {mobile_number} 🔐 Please type the 6-digit OTP."
    USER_INFO_PROMPT = "OTP verified! Please provide the user's details, starting with their First Name."
    ID_PROMPT = "Thanks, {name}! Choose the ID proof type:\n1. PAN\n2. Passport\n3. Driving License\n4. Voter ID"
    PLAN_PROMPT = "Great! Now, select a plan."
    BARCODE_PROMPT = "All images received! ✅ Please select the FASTag serial number."
    VEHICLE_MAKER_PROMPT = "Almost there! Select the vehicle manufacturer."
    CONFIRMATION_PROMPT = "Please review the details and confirm."
    SUCCESS_MESSAGE = "🎉 Success! Your FASTag has been Activated ✅"

# --- Utility Functions ---
def get_session(session_id: str) -> Session:
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or has expired.")
    return session

def extract_request_id(response: Dict[str, Any]) -> Optional[str]:
    """Extracts the request ID from the API response."""
    data = response.get("data")
    if isinstance(data, list) and data:
        return data[0].get("requestId")
    if isinstance(data, dict):
        return data.get("requestId")
    return None

# --- API Endpoints: FASTag Assignment Flow ---

@router.post("/assign/start", summary="Start FASTag Assignment")
def start_assignment(request: SessionRequest):
    session = get_session(request.session_id)
    session_service.update_session(session_id=str(session.session_id), current_state="AWAITING_VEHICLE_DETAILS")
    return {"message": Message.VEHICLE_PROMPT}

@router.post("/assign/vehicle-details", summary="Submit Vehicle and Engine Number")
def submit_vehicle_details(request: VehicleDetailsRequest):
    session = get_session(request.session_id)
    if not all([Validators.validate_vehicle_number(request.vehicle_number), Validators.validate_engine_number(request.engine_number)]):
        raise HTTPException(status_code=400, detail="Invalid vehicle or engine number format.")

    session_service.update_session(
        session_id=str(session.session_id),
        vehicle_number=request.vehicle_number,
        engine_number=request.engine_number,
        current_state="AWAITING_USER_MOBILE"
    )
    return {"message": Message.USER_MOBILE_PROMPT}

@router.post("/assign/user-mobile", summary="Submit User Mobile and Send OTP")
def submit_user_mobile(request: UserMobileRequest):
    session = get_session(request.session_id)
    if not Validators.validate_mobile(request.user_mobile):
        raise HTTPException(status_code=400, detail="Invalid user mobile number format.")

    api_response = shauryapay_api.generate_otp_by_vehicle(
        vehicle_number=str(session.vehicle_number),
        agent_id=int(session.agent_id),
        mobile_number=request.user_mobile,
        engine_no=str(session.engine_number)
    )

    request_id = extract_request_id(api_response)
    shauryapay_session_id = shauryapay_api.extract_session_id(api_response)
    
    if not request_id:
        raise HTTPException(status_code=500, detail=f"Failed to generate OTP from provider: {api_response.get('message', 'Unknown error')}")

    session_service.update_session(
        session_id=str(session.session_id),
        user_mobile=request.user_mobile,
        request_id=request_id,
        shauryapay_session_id=shauryapay_session_id,
        current_state="AWAITING_USER_OTP"
    )
    return {"message": Message.OTP_PROMPT.format(mobile_number=request.user_mobile)}

@router.post("/assign/verify-otp", summary="Verify User OTP")
def verify_user_otp(request: UserOTPRequest):
    session = get_session(request.session_id)
    
    # Use the Shauryapay session ID from the API response
    if session.shauryapay_session_id is None:
        raise HTTPException(status_code=400, detail="No Shauryapay session ID found. Please generate OTP first.")
    
    api_response = shauryapay_api.validate_otp(
        request_id=str(session.request_id),
        session_id=str(session.shauryapay_session_id),  # Use Shauryapay session ID
        agent_id=int(session.agent_id),
        otp=request.otp
    )

    if api_response.get("status") != "true":
        raise HTTPException(status_code=400, detail=api_response.get("message", "Invalid OTP."))

    session_service.update_session(session_id=str(session.session_id), current_state="AWAITING_USER_INFO")
    return {"message": Message.USER_INFO_PROMPT}

@router.post("/assign/user-info", summary="Submit User's Personal Information")
def submit_user_info(request: UserInfoRequest):
    session = get_session(request.session_id)
    session_service.update_session(
        session_id=str(session.session_id),
        first_name=request.first_name,
        last_name=request.last_name,
        dob=request.dob,
        current_state="AWAITING_ID_PROOF"
    )
    return {"message": Message.ID_PROMPT.format(name=request.first_name)}

# ... The rest of the endpoints (ID proof, plan, barcode, etc.) would follow this pattern ...

@router.post("/assign/confirm", summary="Confirm All Details and Activate FASTag")
def confirm_and_activate(request: ConfirmationRequest):
    session = get_session(request.session_id)
    if not request.confirm:
        session_service.update_session(session_id=str(session.session_id), current_state="AWAITING_CORRECTION")
        return {"message": "Please specify which detail you would like to edit."}
    
    session_service.complete_session(str(session.session_id))
    agent_details = agent_service.get_agent_details(int(session.agent_id))
    
    wallet_balance = agent_details.get('wallet_balance', 'N/A') if agent_details else 'N/A'
    fastags_left = agent_details.get('fastags_left', 'N/A') if agent_details else 'N/A'

    response_message = (
        f"{Message.SUCCESS_MESSAGE}\n"
        f"Customer Name: {session.first_name} {session.last_name}\n"
        f"Vehicle No: {session.vehicle_number}\n"
        f"Barcode No: {session.barcode_selected}\n\n"
        "📦 Your FASTag will be shipped shortly!\n"
        f"💼 Wallet Balance: ₹{wallet_balance}\n"
        f"🏷️ FASTags Left: {fastags_left}"
    )

    return {"message": response_message}

# --- API Endpoints: FASTag Replacement Flow ---

@router.post("/replace/start", summary="Start FASTag Replacement")
def start_replacement(request: SessionRequest):
    session = get_session(request.session_id)
    session_service.update_session(session_id=str(session.session_id), current_state="REPLACE_AWAITING_USER_MOBILE")
    return {"message": Message.USER_MOBILE_PROMPT}

@router.post("/replace/verify-mobile", summary="Verify User Mobile for Replacement")
def verify_mobile_for_replacement(request: UserMobileRequest):
    session = get_session(request.session_id)
    if not Validators.validate_mobile_number(request.user_mobile):
        raise HTTPException(status_code=400, detail="Invalid mobile number format.")
    
    # Check if user exists in database
    user_exists = shauryapay_api.check_user_exists(request.user_mobile)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    
    # Generate OTP
    otp_response = shauryapay_api.generate_otp(request.user_mobile)
    if not otp_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to generate OTP.")
    
    session_service.update_session(
        session_id=str(session.session_id),
        user_mobile=request.user_mobile,
        current_state="REPLACE_AWAITING_OTP"
    )
    return {"message": Message.OTP_PROMPT.format(mobile_number=request.user_mobile)}

@router.post("/replace/verify-otp", summary="Verify OTP for Replacement")
def verify_otp_for_replacement(request: UserOTPRequest):
    session = get_session(request.session_id)
    if not Validators.validate_otp(request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP format.")
    
    # Get the mobile number from session
    user_mobile = str(session.user_mobile) if session.user_mobile is not None else None
    if not user_mobile:
        raise HTTPException(status_code=400, detail="User mobile number not found in session.")
    
    # Verify OTP
    verify_response = shauryapay_api.verify_otp(mobile_number=user_mobile, otp=request.otp)
    if not verify_response.get("success"):
        raise HTTPException(status_code=401, detail="Invalid OTP.")
    
    # Get available plans
    plans = shauryapay_api.get_available_plans()
    
    session_service.update_session(
        session_id=str(session.session_id),
        current_state="REPLACE_AWAITING_PLAN"
    )
    
    plans_message = "Please select a plan:\n"
    for plan in plans:
        plans_message += f"{plan['id']}. ₹{plan['amount']} - {plan['description']}\n"
    
    return {"message": plans_message, "plans": plans}

@router.post("/replace/select-plan", summary="Select Plan for Replacement")
def select_plan_for_replacement(request: PlanRequest):
    session = get_session(request.session_id)
    
    # Validate plan selection
    plan = shauryapay_api.get_plan(request.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan selection.")
    
    # Get available barcodes
    barcodes = shauryapay_api.get_available_barcodes()
    if not barcodes:
        raise HTTPException(status_code=404, detail="No barcodes available.")
    
    session_service.update_session(
        session_id=str(session.session_id),
        selected_plan=request.plan_id,
        current_state="REPLACE_AWAITING_BARCODE"
    )
    
    barcodes_message = "Please select a barcode:\n"
    for barcode in barcodes:
        barcodes_message += f"{barcode['id']}. {barcode['number']}\n"
    
    return {"message": barcodes_message, "barcodes": barcodes}

@router.post("/replace/select-barcode", summary="Select Barcode for Replacement")
def select_barcode_for_replacement(request: BarcodeRequest):
    session = get_session(request.session_id)
    
    # Validate barcode selection
    barcode = shauryapay_api.get_barcode(request.barcode)
    if not barcode:
        raise HTTPException(status_code=400, detail="Invalid barcode selection.")
    
    # Get user mobile from session
    user_mobile = str(session.user_mobile) if session.user_mobile is not None else None
    if not user_mobile:
        raise HTTPException(status_code=400, detail="User mobile number not found in session.")
    
    # Get user info
    user_info = shauryapay_api.get_user_info(mobile_number=user_mobile)
    if not user_info:
        raise HTTPException(status_code=404, detail="User information not found.")
    
    session_service.update_session(
        session_id=str(session.session_id),
        barcode_selected=request.barcode,
        current_state="REPLACE_AWAITING_CONFIRMATION"
    )
    
    confirmation_message = (
        "Please review the following details:\n\n"
        f"Customer Name: {user_info['name']}\n"
        f"Mobile: {user_mobile}\n"
        f"Selected Plan: {str(session.selected_plan) if session.selected_plan is not None else 'N/A'}\n"
        f"New Barcode: {request.barcode}\n\n"
        "Type 'confirm' to proceed or 'cancel' to start over."
    )
    
    return {"message": confirmation_message, "user_info": user_info}

@router.post("/replace/confirm", summary="Confirm FASTag Replacement")
def confirm_replacement(request: ConfirmationRequest):
    session = get_session(request.session_id)
    if not request.confirm:
        session_service.update_session(session_id=str(session.session_id), current_state="REPLACE_AWAITING_USER_MOBILE")
        return {"message": "Replacement cancelled. Let's start over with the user's mobile number."}
    
    # Get required values from session
    user_mobile = str(session.user_mobile) if session.user_mobile is not None else None
    barcode_selected = str(session.barcode_selected) if session.barcode_selected is not None else None
    selected_plan = str(session.selected_plan) if session.selected_plan is not None else None
    agent_id = int(session.agent_id) if session.agent_id is not None else None
    
    # Validate required values
    if not all([user_mobile, barcode_selected, selected_plan, agent_id]):
        raise HTTPException(status_code=400, detail="Missing required session data.")
    
    # Process the replacement
    if not all([isinstance(user_mobile, str), isinstance(barcode_selected, str), isinstance(selected_plan, str)]):
        raise HTTPException(status_code=400, detail="Invalid session data types.")
    
    replacement_response = shauryapay_api.process_replacement(
        user_mobile=user_mobile,
        new_barcode=barcode_selected,
        plan_id=selected_plan
    )
    
    if not replacement_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to process replacement.")
    
    # Get agent details for the success message
    agent_details = agent_service.get_agent_details(agent_id=agent_id)
    wallet_balance = agent_details.get('wallet_balance', 'N/A') if agent_details else 'N/A'
    fastags_left = agent_details.get('fastags_left', 'N/A') if agent_details else 'N/A'
    
    session_service.complete_session(str(session.session_id))
    
    success_message = (
        "🎉 Success! FASTag has been replaced successfully!\n\n"
        f"Customer Mobile: {user_mobile}\n"
        f"New Barcode: {barcode_selected}\n\n"
        f"💼 Wallet Balance: ₹{wallet_balance}\n"
        f"🏷️ FASTags Left: {fastags_left}"
    )
    
    return {"message": success_message} 