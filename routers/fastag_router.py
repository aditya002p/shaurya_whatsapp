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

# Add this model for image upload
class ImageUploadRequest(SessionRequest):
    image_type: str  # e.g., 'rc_front', 'rc_back', etc.
    image_base64: str

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

@router.post("/assign/id-proof", summary="Submit User's ID Proof")
def submit_id_proof(request: IdProofRequest):
    session = get_session(request.session_id)
    # Save ID proof info in session
    session_service.update_session(
        session_id=str(session.session_id),
        id_type=request.id_type,
        id_number=request.id_number,
        expiry_date=request.expiry_date,
        current_state="AWAITING_PLAN"
    )
    return {"message": Message.PLAN_PROMPT}

# --- FASTag Assignment Flow ---

@router.post("/assign/plan", summary="Select Plan")
def select_plan(request: PlanRequest):
    session = get_session(request.session_id)
    # Fetch available plans from Shauryapay API
    plans_response = shauryapay_api.get_available_plans(agent_id=session.agent_id)
    if not plans_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to fetch plans.")
    plans = plans_response.get("plans", [])
    if not any(plan['id'] == request.plan_id for plan in plans):
        raise HTTPException(status_code=400, detail="Invalid plan selected.")
    session_service.update_session(
        session_id=str(session.session_id),
        plan_id=request.plan_id,
        current_state="AWAITING_DOCUMENT_UPLOAD"
    )
    plans_message = "Please select a plan:\n"
    for plan in plans:
        plans_message += f"{plan['id']}. ₹{plan['amount']} - {plan['description']}\n"
    return {"message": plans_message, "plans": plans}

@router.post("/assign/upload-image", summary="Upload Document/Image")
def upload_image(request: ImageUploadRequest):
    session = get_session(request.session_id)
    # Validate image type
    allowed_types = ['rc_front', 'rc_back', 'vehicle_front', 'vehicle_side', 'tag_fixed']
    if request.image_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image type.")
    # Upload image to Shauryapay
    api_response = shauryapay_api.upload_document(
        session_id=session.shauryapay_session_id,
        image_type=request.image_type,
        image_base64=request.image_base64
    )
    if not api_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to upload image.")
    # Track uploaded images in session if needed
    session_service.update_session(
        session_id=str(session.session_id),
        current_state="AWAITING_MORE_IMAGES"
    )
    return {"message": "Image received. Please upload the next image or type 'done' if all images are uploaded."}

@router.post("/assign/images-done", summary="All Images Uploaded")
def images_done(request: SessionRequest):
    session = get_session(request.session_id)
    # Move to barcode selection
    session_service.update_session(
        session_id=str(session.session_id),
        current_state="AWAITING_BARCODE_SELECTION"
    )
    # Fetch available barcodes from Shauryapay API
    barcodes_response = shauryapay_api.get_available_barcodes(agent_id=session.agent_id)
    if not barcodes_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to fetch barcodes.")
    barcodes = barcodes_response.get("barcodes", [])
    barcodes_message = "Available Barcodes:\n" + "\n".join([b['barcode'] for b in barcodes])
    return {"message": barcodes_message, "barcodes": barcodes}

@router.post("/assign/barcode", summary="Select Barcode")
def select_barcode(request: BarcodeRequest):
    session = get_session(request.session_id)
    # Validate barcode
    barcodes_response = shauryapay_api.get_available_barcodes(agent_id=session.agent_id)
    barcodes = barcodes_response.get("barcodes", [])
    if not any(b['barcode'] == request.barcode for b in barcodes):
        raise HTTPException(status_code=400, detail="Invalid barcode selected.")
    session_service.update_session(
        session_id=str(session.session_id),
        barcode_selected=request.barcode,
        current_state="AWAITING_VEHICLE_MAKER"
    )
    # Fetch vehicle makers
    makers_response = shauryapay_api.get_vehicle_makers(session_id=session.shauryapay_session_id, agent_id=session.agent_id, vehicle_number=session.vehicle_number)
    if not makers_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to fetch vehicle makers.")
    makers = makers_response.get("makers", [])
    makers_message = "Who is your Vehicle Maker?\n" + "\n".join(makers)
    return {"message": makers_message, "makers": makers}

@router.post("/assign/vehicle_maker", summary="Select Vehicle Maker")
def select_vehicle_maker(request: VehicleInfoRequest):
    session = get_session(request.session_id)
    makers_response = shauryapay_api.get_vehicle_makers(session_id=session.shauryapay_session_id, agent_id=session.agent_id, vehicle_number=session.vehicle_number)
    makers = makers_response.get("makers", [])
    if request.maker not in makers:
        raise HTTPException(status_code=400, detail="Invalid vehicle maker.")
    session_service.update_session(
        session_id=str(session.session_id),
        maker=request.maker,
        current_state="AWAITING_VEHICLE_MODEL"
    )
    models_response = shauryapay_api.get_vehicle_models(maker=request.maker)
    if not models_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to fetch vehicle models.")
    models = models_response.get("models", [])
    models_message = "What is your Vehicle Model?\n" + "\n".join(models)
    return {"message": models_message, "models": models}

@router.post("/assign/vehicle_model", summary="Select Vehicle Model")
def select_vehicle_model(request: VehicleInfoRequest):
    session = get_session(request.session_id)
    models_response = shauryapay_api.get_vehicle_models(maker=session.maker)
    models = models_response.get("models", [])
    if request.model not in models:
        raise HTTPException(status_code=400, detail="Invalid vehicle model.")
    session_service.update_session(
        session_id=str(session.session_id),
        model=request.model,
        current_state="AWAITING_VEHICLE_DESCRIPTOR"
    )
    descriptors_response = shauryapay_api.get_vehicle_descriptors(model=request.model)
    if not descriptors_response.get("success"):
        raise HTTPException(status_code=500, detail="Failed to fetch vehicle descriptors.")
    descriptors = descriptors_response.get("descriptors", [])
    descriptors_message = "What is your Vehicle Descriptor?\n" + "\n".join(descriptors)
    return {"message": descriptors_message, "descriptors": descriptors}

@router.post("/assign/vehicle_descriptor", summary="Select Vehicle Descriptor")
def select_vehicle_descriptor(request: VehicleInfoRequest):
    session = get_session(request.session_id)
    descriptors_response = shauryapay_api.get_vehicle_descriptors(model=session.model)
    descriptors = descriptors_response.get("descriptors", [])
    if request.descriptor not in descriptors:
        raise HTTPException(status_code=400, detail="Invalid vehicle descriptor.")
    session_service.update_session(
        session_id=str(session.session_id),
        descriptor=request.descriptor,
        current_state="AWAITING_CONFIRMATION"
    )
    # Show confirmation message
    confirmation_message = (
        "Checkout Details & edit if required\n"
        f"Vehicle no - {session.vehicle_number}\n"
        f"Phone no - {session.user_mobile}\n"
        f"Last 5 digits of engine no - {session.engine_number}\n"
        f"Aadhar No - {session.id_number}\n"
        f"Plan - {session.plan_id}\n"
        f"Vehicle Maker - {session.maker}\n"
        f"Vehicle Model - {session.model}\n"
        f"Vehicle Descriptor - {request.descriptor}\n"
        "Confirm if entered details are correct with Yes or No?"
    )
    return {"message": confirmation_message}

@router.post("/assign/confirm", summary="Confirm All Details and Activate FASTag")
def confirm_and_activate(request: ConfirmationRequest):
    session = get_session(request.session_id)
    if not request.confirm:
        session_service.update_session(session_id=str(session.session_id), current_state="AWAITING_CORRECTION")
        return {"message": "Please specify which detail you would like to edit."}
    # Call Shauryapay API to activate FASTag
    activation_response = shauryapay_api.activate_fastag(
        session_id=session.shauryapay_session_id,
        agent_id=session.agent_id,
        vehicle_number=session.vehicle_number,
        barcode=session.barcode_selected,
        plan_id=session.plan_id,
        maker=session.maker,
        model=session.model,
        descriptor=session.descriptor,
        id_type=session.id_type,
        id_number=session.id_number,
        expiry_date=session.expiry_date,
        first_name=session.first_name,
        last_name=session.last_name,
        dob=session.dob,
        user_mobile=session.user_mobile,
        # Add any other required fields from your API spec
    )
    if not activation_response.get("success"):
        raise HTTPException(status_code=500, detail=activation_response.get("message", "Failed to activate FASTag."))
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