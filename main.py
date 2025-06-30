import re
import base64
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

from config import Config
from services.session_service import SessionService
from services.agent_service import AgentService
from services.shauryapay_api import ShauryapayAPI
from utils.validators import Validators

# Import routers
from routers.agent_router import router as agent_router
from routers.session_router import router as session_router
from routers.vehicle_router import router as vehicle_router
from routers.fastag_router import router as fastag_router

app = FastAPI(title="FASTag WhatsApp/Interakt Backend")

# Include routers
app.include_router(agent_router)
app.include_router(session_router)
app.include_router(vehicle_router)
app.include_router(fastag_router)

# Initialize services
session_service = SessionService()
agent_service = AgentService()
shauryapay_api = ShauryapayAPI()
validators = Validators()

class WhatsAppMessage(BaseModel):
    object: str
    entry: list

class MessageData(BaseModel):
    messaging_product: str
    metadata: Dict[str, Any]
    contacts: list
    messages: list

class BotHandler:
    def __init__(self):
        self.session_service = session_service
        self.agent_service = agent_service
        self.shauryapay_api = shauryapay_api
        self.validators = validators
    
    def get_welcome_message(self, agent_name: str, wallet_balance: int, fastags_left: int) -> str:
        """Generate welcome message with agent info"""
        return f"""Hi {agent_name}👋,
💼Your Wallet Balance: ₹{wallet_balance}, 🏷️ FASTags Left: {fastags_left}
Let's get your FASTag in just a few steps. 🚗
Please enter your Vehicle Number (e.g., MH12AB1234)"""
    
    def get_engine_number_prompt(self) -> str:
        """Prompt for engine number"""
        return "Got it ✅Share the last 5 digits of engine no."
    
    def get_mobile_number_prompt(self) -> str:
        """Prompt for mobile number"""
        return "Now send your 10-digit Mobile Number:"
    
    def get_otp_sent_message(self, mobile: str) -> str:
        """Message when OTP is sent"""
        return f"""Sending OTP to your {mobile} 🔐
Please type the 6-digit OTP
🔁 Didn't get the OTP? Reply Resend"""
    
    def get_first_name_prompt(self) -> str:
        """Prompt for first name"""
        return "Share your FirstName"
    
    def get_last_name_prompt(self) -> str:
        """Prompt for last name"""
        return "Share your LastName"
    
    def get_dob_prompt(self) -> str:
        """Prompt for date of birth"""
        return "Share your DOB (DD-MM-YYYY)/(Date-Month-Year)"
    
    def get_id_proof_prompt(self) -> str:
        """Prompt for ID proof selection"""
        return """Choose your ID Proof type:

1. PAN
2. Passport no  - ask for expiry date
3. Driving License - expiry date
4. Voter Id 
Select any one of above 
(Type 1, 2, 3, or 4)"""
    
    def get_id_proof_number_prompt(self, id_type: str) -> str:
        """Prompt for ID proof number based on type"""
        if id_type == "PAN":
            return "Enter your Aadhaar Number:"
        elif id_type == "Passport":
            return "Enter your Passport Number:"
        elif id_type == "Driving License":
            return "Enter your Driving License Number:"
        elif id_type == "Voter ID":
            return "Enter your Voter ID Number:"
        return "Enter your ID Number:"
    
    def get_plan_selection_prompt(self) -> str:
        """Prompt for plan selection"""
        return """Select your Plan:
400 Plan
500 Plan
Sat/Sun - limited offer no other offers"""
    
    def get_wallet_creation_result(self, success: bool) -> str:
        """Message for wallet creation result"""
        if success:
            return "User Wallet Created Successfully"
        else:
            return "Failed to Create User Wallet as ID proof is linked to another mobile number or the Aadhaar number may be incorrect. Please check and try again."
    
    def get_document_upload_prompt(self, doc_type: str) -> str:
        """Prompt for document upload"""
        doc_names = {
            "RC_FRONT": "📄 RC Front",
            "RC_BACK": "📄 RC Back", 
            "VEHICLE_FRONT": "📸 Vehicle Front",
            "VEHICLE_SIDE": "📸 Vehicle Side",
            "TAG_FIXED": "📸 Tag Fixed (If available)"
        }
        return f"Now please send the following 5 images one by one:\n{doc_names.get(doc_type, doc_type)}"
    
    def get_all_images_received_message(self) -> str:
        """Message when all images are received"""
        return "✅ All images received! \nEnter Last 4 digits of Serial Number(Barcode)"
    
    def get_barcode_selection_prompt(self, barcodes: list) -> str:
        """Prompt for barcode selection"""
        barcode_list = "\n".join(barcodes)
        return f"Available Barcodes: \n{barcode_list}"
    
    def get_vehicle_maker_prompt(self) -> str:
        """Prompt for vehicle maker selection"""
        makers = "\n".join(Config.VEHICLE_MANUFACTURERS.keys())
        return f"Who is your Vehicle Maker?\n{makers}"
    
    def get_vehicle_model_prompt(self, maker: str) -> str:
        """Prompt for vehicle model selection"""
        models = Config.VEHICLE_MODELS.get(maker, [])
        if models:
            model_list = "\n".join(models)
            return f"What is your Vehicle Model?\n{model_list}"
        return "What is your Vehicle Model?"
    
    def get_vehicle_descriptor_prompt(self) -> str:
        """Prompt for vehicle descriptor"""
        descriptors = "\n".join(Config.VEHICLE_DESCRIPTORS)
        return f"What is your Vehicle Descriptor\n{descriptors}"
    
    def get_confirmation_prompt(self, session_data: Dict[str, Any]) -> str:
        """Generate confirmation prompt with all details"""
        return f"""Checkout Details & edit if required
Vehicle no - {session_data.get('vehicle_number', 'N/A')} 
Phone no - {session_data.get('mobile_number', 'N/A')}
Last 5 digits of engine no - {session_data.get('engine_number', 'N/A')}
Aadhar No - {session_data.get('id_proof_number', 'N/A')}
Plan - {session_data.get('plan_selected', 'N/A')}
Vehicle Maker - {session_data.get('vehicle_maker', 'N/A')} 
Vehicle Model - {session_data.get('vehicle_model', 'N/A')}
Vehicle Descriptor - {session_data.get('vehicle_descriptor', 'N/A')}
Confirm if entered details are correct with Yes or No?"""
    
    def get_success_message(self) -> str:
        """Success message when FASTag is activated"""
        return "🎉 Success! Your FASTag has been Activated ✅"
    
    def get_error_message(self, error: str) -> str:
        """Error message"""
        return f"❌ Error: {error}"
    
    def process_message(self, user_mobile: str, message_text: str, 
                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main message processing logic following the bot flow
        """
        try:
            # Get or create session
            if not session_id:
                # For demo, using agent_id = 1, you should implement proper agent detection
                session = self.session_service.create_session(agent_id=1, user_mobile=user_mobile)
                session_id = session["session_id"]
            else:
                session = self.session_service.get_session(session_id)
                if not session:
                    return {"error": "Session not found"}
            
            current_state = session["current_state"]
            
            # Ensure session_id is not None
            if not session_id:
                return {"error": "Invalid session"}
            
            # Handle different states
            if current_state == Config.SESSION_STATES["INIT"]:
                return self.handle_init_state(session_id, user_mobile, message_text)
            elif current_state == Config.SESSION_STATES["AGENT_MOBILE"]:
                return self.handle_agent_mobile(session_id, message_text)
            elif current_state == Config.SESSION_STATES["AGENT_OTP"]:
                return self.handle_agent_otp(session_id, message_text)
            elif current_state == Config.SESSION_STATES["AGENT_VERIFIED"]:
                return self.handle_agent_verified(session_id, message_text)
            elif current_state == Config.SESSION_STATES["VEHICLE_NUMBER"]:
                return self.handle_vehicle_number(session_id, message_text)
            elif current_state == Config.SESSION_STATES["ENGINE_NUMBER"]:
                return self.handle_engine_number(session_id, message_text)
            elif current_state == Config.SESSION_STATES["MOBILE_NUMBER"]:
                return self.handle_mobile_number(session_id, message_text)
            elif current_state == Config.SESSION_STATES["OTP_SENT"]:
                return self.handle_otp_verification(session_id, message_text)
            elif current_state == Config.SESSION_STATES["OTP_VERIFIED"]:
                return self.handle_otp_verified(session_id, message_text)
            elif current_state == Config.SESSION_STATES["FIRST_NAME"]:
                return self.handle_first_name(session_id, message_text)
            elif current_state == Config.SESSION_STATES["LAST_NAME"]:
                return self.handle_last_name(session_id, message_text)
            elif current_state == Config.SESSION_STATES["DOB"]:
                return self.handle_dob(session_id, message_text)
            elif current_state == Config.SESSION_STATES["ID_PROOF_TYPE"]:
                return self.handle_id_proof_type(session_id, message_text)
            elif current_state == Config.SESSION_STATES["ID_PROOF_NUMBER"]:
                return self.handle_id_proof_number(session_id, message_text)
            elif current_state == Config.SESSION_STATES["PLAN_SELECTION"]:
                return self.handle_plan_selection(session_id, message_text)
            elif current_state == Config.SESSION_STATES["WALLET_CREATED"]:
                return self.handle_wallet_created(session_id, message_text)
            elif current_state in [Config.SESSION_STATES["RC_FRONT"], 
                                 Config.SESSION_STATES["RC_BACK"],
                                 Config.SESSION_STATES["VEHICLE_FRONT"],
                                 Config.SESSION_STATES["VEHICLE_SIDE"],
                                 Config.SESSION_STATES["TAG_FIXED"]]:
                return self.handle_document_upload(session_id, current_state, message_text)
            elif current_state == Config.SESSION_STATES["SERIAL_NUMBER"]:
                return self.handle_serial_number(session_id, message_text)
            elif current_state == Config.SESSION_STATES["BARCODE_SELECTION"]:
                return self.handle_barcode_selection(session_id, message_text)
            elif current_state == Config.SESSION_STATES["VEHICLE_MAKER"]:
                return self.handle_vehicle_maker(session_id, message_text)
            elif current_state == Config.SESSION_STATES["VEHICLE_MODEL"]:
                return self.handle_vehicle_model(session_id, message_text)
            elif current_state == Config.SESSION_STATES["VEHICLE_DESCRIPTOR"]:
                return self.handle_vehicle_descriptor(session_id, message_text)
            elif current_state == Config.SESSION_STATES["CONFIRMATION"]:
                return self.handle_confirmation(session_id, message_text)
            # Replace FASTag flow states
            elif current_state == Config.SESSION_STATES["REPLACE_USER_MOBILE"]:
                return self.handle_replace_user_mobile(session_id, message_text)
            elif current_state == Config.SESSION_STATES["REPLACE_USER_OTP"]:
                return self.handle_replace_user_otp(session_id, message_text)
            elif current_state == Config.SESSION_STATES["REPLACE_USER_VERIFIED"]:
                return self.handle_replace_user_verified(session_id, message_text)
            elif current_state == Config.SESSION_STATES["REPLACE_PLAN_SELECTION"]:
                return self.handle_replace_plan_selection(session_id, message_text)
            elif current_state == Config.SESSION_STATES["REPLACE_BARCODE_SELECTION"]:
                return self.handle_replace_barcode_selection(session_id, message_text)
            elif current_state == Config.SESSION_STATES["REPLACE_CONFIRMATION"]:
                return self.handle_replace_confirmation(session_id, message_text)
            else:
                return {"error": "Invalid state"}
                
        except Exception as e:
            return {"error": f"Processing error: {str(e)}"}
    
    def handle_init_state(self, session_id: str, user_mobile: str, message_text: str) -> Dict[str, Any]:
        """Handle initial state - ask for agent mobile number"""
        # For Interakt integration, start with agent verification
        self.session_service.update_session_state(session_id, Config.SESSION_STATES["AGENT_MOBILE"])
        return {"message": "Please enter your registered mobile number to continue."}
    
    def handle_agent_mobile(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle agent mobile number input"""
        if self.validators.validate_mobile_number(message_text):
            # Check if agent exists
            agent = self.agent_service.get_by_mobile(message_text)
            if agent:
                # Generate OTP for agent
                otp = self.agent_service.send_otp(message_text)
                if otp:
                    self.session_service.update_session_data(session_id, agent_mobile=message_text, agent_id=agent.id)
                    self.session_service.update_session_state(session_id, Config.SESSION_STATES["AGENT_OTP"])
                    return {"message": f"OTP sent to your mobile. Please enter the 4-digit OTP. (Demo OTP: {otp})"}
                else:
                    return {"error": "Failed to send OTP. Please try again."}
            else:
                return {"error": "Agent number is wrong. Please use a different mobile number."}
        else:
            return {"error": "Invalid mobile number. Please enter 10-digit number."}
    
    def handle_agent_otp(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle agent OTP verification"""
        if self.validators.validate_otp(message_text):
            session = self.session_service.get_session(session_id)
            if session and session.get("agent_mobile"):
                # Verify OTP
                if self.agent_service.verify_otp(session["agent_mobile"], message_text):
                    agent = self.agent_service.get_by_mobile(session["agent_mobile"])
                    if agent:
                        self.session_service.update_session_state(session_id, Config.SESSION_STATES["AGENT_VERIFIED"])
                        return {
                            "message": f"Hi {agent.first_name} 👋,\n💼Your Wallet Balance: ₹{agent.wallet_balance}, 🏷️ FASTags Left: {agent.fastags_left}",
                            "options": ["Assign a FASTag", "Replace a FASTag"]
                        }
                    else:
                        return {"error": "Agent not found"}
                else:
                    return {"error": "Invalid OTP. Please try again."}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid OTP format. Please enter 4-digit OTP."}
    
    def handle_agent_verified(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle agent verification - show options and start FASTag assignment"""
        if message_text.lower() in ["assign a fastag", "assign", "1"]:
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["VEHICLE_NUMBER"])
            return {"message": "Let's get your FASTag in just a few steps. 🚗\nPlease enter your Vehicle Number (e.g., MH12AB1234)"}
        elif message_text.lower() in ["replace a fastag", "replace", "2"]:
            # Start replace FASTag flow
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_USER_MOBILE"])
            return {"message": "Let's replace your FASTag! 🔄\nPlease enter the user's mobile number:"}
        else:
            return {"error": "Please choose 'Assign a FASTag' or 'Replace a FASTag'"}
    
    def handle_vehicle_number(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle vehicle number input"""
        if self.validators.validate_vehicle_number(message_text):
            self.session_service.update_session_data(session_id, vehicle_number=message_text)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["ENGINE_NUMBER"])
            return {"message": self.get_engine_number_prompt()}
        else:
            return {"error": "Invalid vehicle number format. Please enter in format like MH12AB1234"}
    
    def handle_engine_number(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle engine number input"""
        if self.validators.validate_engine_number(message_text):
            self.session_service.update_session_data(session_id, engine_number=message_text)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["MOBILE_NUMBER"])
            return {"message": self.get_mobile_number_prompt()}
        else:
            return {"error": "Invalid engine number. Please enter last 5 digits only."}
    
    def handle_mobile_number(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle mobile number input and generate OTP"""
        if self.validators.validate_mobile_number(message_text):
            session = self.session_service.get_session(session_id)
            if session:
                # Call Shauryapay API to generate OTP
                response = self.shauryapay_api.generate_otp_by_vehicle(
                    vehicle_number=session["vehicle_number"],
                    agent_id=session["agent_id"],
                    mobile_number=message_text,
                    engine_no=session["engine_number"]
                )
                
                if response.get("status") == "true":
                    # Store request_id and session_id from API response
                    data = response.get("data", [{}])[0]
                    self.session_service.update_session_data(
                        session_id, 
                        mobile_number=message_text,
                        request_id=data.get("requestId"),
                        shauryapay_session_id=data.get("sessionId")
                    )
                    self.session_service.update_session_state(session_id, Config.SESSION_STATES["OTP_SENT"])
                    return {"message": self.get_otp_sent_message(message_text)}
                else:
                    return {"error": f"Failed to generate OTP: {response.get('message', 'Unknown error')}"}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid mobile number. Please enter 10-digit number."}
    
    def handle_otp_verification(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle OTP verification"""
        if message_text.lower() == "resend":
            # Handle resend OTP logic
            return {"message": "OTP resent successfully. Please check your mobile."}
        
        if self.validators.validate_otp(message_text):
            session = self.session_service.get_session(session_id)
            if session:
                # Call Shauryapay API to validate OTP
                response = self.shauryapay_api.validate_otp(
                    request_id=session["request_id"],
                    session_id=session["shauryapay_session_id"],
                    agent_id=session["agent_id"],
                    otp=message_text
                )
                
                if response.get("status") == "true":
                    self.session_service.update_session_state(session_id, Config.SESSION_STATES["OTP_VERIFIED"])
                    return {"message": self.get_first_name_prompt()}
                else:
                    return {"error": f"Invalid OTP: {response.get('message', 'Please try again')}"}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid OTP format. Please enter 6-digit OTP."}
    
    def handle_otp_verified(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle post OTP verification - ask for first name"""
        if message_text.strip():
            self.session_service.update_session_data(session_id, first_name=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["FIRST_NAME"])
            return {"message": self.get_last_name_prompt()}
        else:
            return {"error": "Please enter your first name."}
    
    def handle_first_name(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle first name input"""
        if message_text.strip():
            self.session_service.update_session_data(session_id, first_name=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["LAST_NAME"])
            return {"message": self.get_last_name_prompt()}
        else:
            return {"error": "Please enter your first name."}
    
    def handle_last_name(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle last name input"""
        if message_text.strip():
            self.session_service.update_session_data(session_id, last_name=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["DOB"])
            return {"message": self.get_dob_prompt()}
        else:
            return {"error": "Please enter your last name."}
    
    def handle_dob(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle date of birth input"""
        if self.validators.validate_dob(message_text):
            self.session_service.update_session_data(session_id, dob=message_text)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["ID_PROOF_TYPE"])
            return {"message": self.get_id_proof_prompt()}
        else:
            return {"error": "Invalid date format. Please use DD-MM-YYYY or DD Month YYYY format."}
    
    def handle_id_proof_type(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle ID proof type selection"""
        id_type = Config.ID_PROOF_TYPES.get(message_text.strip())
        if id_type:
            self.session_service.update_session_data(session_id, id_proof_type=id_type)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["ID_PROOF_NUMBER"])
            return {"message": self.get_id_proof_number_prompt(id_type)}
        else:
            return {"error": "Invalid selection. Please choose 1, 2, 3, or 4."}
    
    def handle_id_proof_number(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle ID proof number input"""
        if message_text.strip():
            self.session_service.update_session_data(session_id, id_proof_number=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["PLAN_SELECTION"])
            return {"message": self.get_plan_selection_prompt()}
        else:
            return {"error": "Please enter your ID number."}
    
    def handle_plan_selection(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle plan selection"""
        plan = message_text.strip()
        if "400" in plan or "500" in plan:
            self.session_service.update_session_data(session_id, plan_selected=plan)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["WALLET_CREATED"])
            
            # Call Shauryapay API to create wallet
            session = self.session_service.get_session(session_id)
            if session:
                response = self.shauryapay_api.update_customer_details(
                    vehicle_number=session["vehicle_number"],
                    session_id=session["shauryapay_session_id"],
                    name=session["first_name"],
                    last_name=session["last_name"],
                    dob=session["dob"],
                    doc_type=session["id_proof_type"],
                    doc_no=session["id_proof_number"],
                    plan_id="1" if "400" in plan else "2"
                )
                
                success = response.get("status") == "true"
                return {"message": self.get_wallet_creation_result(success)}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid plan selection. Please choose 400 Plan or 500 Plan."}
    
    def handle_wallet_created(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle post wallet creation - start document upload"""
        self.session_service.update_session_state(session_id, Config.SESSION_STATES["RC_FRONT"])
        return {"message": self.get_document_upload_prompt("RC_FRONT")}
    
    def handle_document_upload(self, session_id: str, current_state: str, message_text: str) -> Dict[str, Any]:
        """Handle document uploads"""
        # In a real implementation, you would handle image uploads here
        # For now, we'll simulate successful upload
        
        # Map states to next states
        state_transitions = {
            Config.SESSION_STATES["RC_FRONT"]: Config.SESSION_STATES["RC_BACK"],
            Config.SESSION_STATES["RC_BACK"]: Config.SESSION_STATES["VEHICLE_FRONT"],
            Config.SESSION_STATES["VEHICLE_FRONT"]: Config.SESSION_STATES["VEHICLE_SIDE"],
            Config.SESSION_STATES["VEHICLE_SIDE"]: Config.SESSION_STATES["TAG_FIXED"],
            Config.SESSION_STATES["TAG_FIXED"]: Config.SESSION_STATES["SERIAL_NUMBER"]
        }
        
        next_state = state_transitions.get(current_state)
        if next_state:
            if next_state == Config.SESSION_STATES["SERIAL_NUMBER"]:
                self.session_service.update_session_state(session_id, next_state)
                return {"message": self.get_all_images_received_message()}
            else:
                self.session_service.update_session_state(session_id, next_state)
                return {"message": self.get_document_upload_prompt(next_state)}
        else:
            return {"error": "Invalid document upload state"}
    
    def handle_serial_number(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle serial number input"""
        if len(message_text.strip()) == 4 and message_text.strip().isdigit():
            self.session_service.update_session_data(session_id, serial_number=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["BARCODE_SELECTION"])
            
            # Get available barcodes
            response = self.shauryapay_api.get_available_barcodes(message_text.strip())
            barcodes = response.get("data", {}).get("available_barcodes", [])
            return {"message": self.get_barcode_selection_prompt(barcodes)}
        else:
            return {"error": "Invalid serial number. Please enter 4 digits only."}
    
    def handle_barcode_selection(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle barcode selection"""
        # In a real implementation, validate against available barcodes
        self.session_service.update_session_data(session_id, barcode_selected=message_text.strip())
        self.session_service.update_session_state(session_id, Config.SESSION_STATES["VEHICLE_MAKER"])
        return {"message": self.get_vehicle_maker_prompt()}
    
    def handle_vehicle_maker(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle vehicle maker selection"""
        maker = message_text.strip().upper()
        if maker in Config.VEHICLE_MANUFACTURERS:
            self.session_service.update_session_data(session_id, vehicle_maker=maker)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["VEHICLE_MODEL"])
            return {"message": self.get_vehicle_model_prompt(maker)}
        else:
            return {"error": "Invalid vehicle maker. Please select from the list."}
    
    def handle_vehicle_model(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle vehicle model selection"""
        if message_text.strip():
            self.session_service.update_session_data(session_id, vehicle_model=message_text.strip())
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["VEHICLE_DESCRIPTOR"])
            return {"message": self.get_vehicle_descriptor_prompt()}
        else:
            return {"error": "Please enter your vehicle model."}
    
    def handle_vehicle_descriptor(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle vehicle descriptor selection"""
        descriptor = message_text.strip()
        if descriptor in Config.VEHICLE_DESCRIPTORS:
            self.session_service.update_session_data(session_id, vehicle_descriptor=descriptor)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["CONFIRMATION"])
            
            # Get session data for confirmation
            session = self.session_service.get_session(session_id)
            if session:
                return {"message": self.get_confirmation_prompt(session)}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid vehicle descriptor. Please select from the list."}
    
    def handle_confirmation(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle final confirmation"""
        if message_text.lower() == "yes":
            # Call Shauryapay API to activate FASTag
            session = self.session_service.get_session(session_id)
            if session:
                response = self.shauryapay_api.activate_fastag(
                    session_id=session["shauryapay_session_id"],
                    barcode=session["barcode_selected"]
                )
                
                if response.get("status") == "true":
                    self.session_service.complete_session(session_id)
                    return {"message": self.get_success_message()}
                else:
                    return {"error": f"Failed to activate FASTag: {response.get('message', 'Unknown error')}"}
            else:
                return {"error": "Session not found"}
        elif message_text.lower() == "no":
            # Handle edit request - for simplicity, restart the flow
            return {"message": "Please start over with your vehicle number."}
        else:
            return {"error": "Please answer with Yes or No."}

    # Replace FASTag Flow Handlers
    
    def handle_replace_user_mobile(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle user mobile number input for replace FASTag"""
        if self.validators.validate_mobile_number(message_text):
            # Store user mobile number
            self.session_service.update_session_data(session_id, replace_user_mobile=message_text)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_USER_OTP"])
            
            # Generate OTP using Shauryapay API (simulate for now)
            # In production, call the actual Shauryapay API
            return {"message": f"Sending OTP to {message_text} 🔐\nPlease type the 6-digit OTP\n🔁 Didn't get the OTP? Reply Resend"}
        else:
            return {"error": "Invalid mobile number. Please enter 10-digit number."}
    
    def handle_replace_user_otp(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle user OTP verification for replace FASTag"""
        if message_text.lower() == "resend":
            return {"message": "OTP resent successfully. Please check your mobile."}
        
        if self.validators.validate_otp(message_text):
            # Verify OTP using Shauryapay API (simulate for now)
            # In production, call the actual Shauryapay API
            session = self.session_service.get_session(session_id)
            if session:
                # For demo, accept any OTP
                self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_USER_VERIFIED"])
                return {"message": "OTP verified successfully! ✅"}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid OTP format. Please enter 6-digit OTP."}
    
    def handle_replace_user_verified(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle post OTP verification for replace FASTag"""
        session = self.session_service.get_session(session_id)
        if session:
            # Check if user exists and show available plans
            # For demo, assume user exists and show plans
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_PLAN_SELECTION"])
            return {"message": "User verified! ✅\n\nSelect your Plan:\n400 Plan\n500 Plan\nSat/Sun - limited offer no other offers"}
        else:
            return {"error": "Session not found"}
    
    def handle_replace_plan_selection(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle plan selection for replace FASTag"""
        plan = message_text.strip()
        if "400" in plan or "500" in plan:
            self.session_service.update_session_data(session_id, replace_plan_selected=plan)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_BARCODE_SELECTION"])
            
            # Get available barcodes for the agent
            session = self.session_service.get_session(session_id)
            if session:
                # Mock barcodes - in production, get from actual API
                barcodes = ["928314081094", "928384281094", "123314081094"]
                barcode_list = "\n".join(barcodes)
                return {"message": f"Available Barcodes:\n{barcode_list}"}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Invalid plan selection. Please choose 400 Plan or 500 Plan."}
    
    def handle_replace_barcode_selection(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle barcode selection for replace FASTag"""
        barcode = message_text.strip()
        if barcode:
            self.session_service.update_session_data(session_id, replace_barcode_selected=barcode)
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_CONFIRMATION"])
            
            # Get session data for confirmation
            session = self.session_service.get_session(session_id)
            if session:
                return {"message": f"Replace FASTag Confirmation:\n\nUser Mobile: {session.get('replace_user_mobile', 'N/A')}\nPlan: {session.get('replace_plan_selected', 'N/A')}\nNew Barcode: {barcode}\n\nConfirm replacement with Yes or No?"}
            else:
                return {"error": "Session not found"}
        else:
            return {"error": "Please select a valid barcode."}
    
    def handle_replace_confirmation(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Handle final confirmation for replace FASTag"""
        if message_text.lower() == "yes":
            session = self.session_service.get_session(session_id)
            if session:
                # Update FASTag in database (simulate for now)
                # In production, call actual API to replace FASTag
                new_barcode = session.get("replace_barcode_selected", "N/A")
                user_mobile = session.get("replace_user_mobile", "N/A")
                
                # Get agent info for final message
                agent = self.agent_service.get_agent_by_id(session.get("agent_id", 1))
                if agent:
                    agent_name = f"{agent.first_name} {agent.last_name}"
                    wallet_balance = agent.wallet_balance
                    fastags_left = agent.fastags_left
                else:
                    agent_name = "Agent"
                    wallet_balance = 0
                    fastags_left = 0
                
                # Mark session as completed
                self.session_service.complete_session(session_id)
                
                return {
                    "message": f"🎉 Success! Your FASTag has been Replaced ✅\n\nNew Barcode Number: {new_barcode}\nUser Mobile: {user_mobile}\n\n💼 Wallet Balance: ₹{wallet_balance}\n🏷️ FASTags Left: {fastags_left}\nLet's continue with the next one. 🚗"
                }
            else:
                return {"error": "Session not found"}
        elif message_text.lower() == "no":
            # Restart replace flow
            self.session_service.update_session_state(session_id, Config.SESSION_STATES["REPLACE_USER_MOBILE"])
            return {"message": "Let's start over with the user's mobile number."}
        else:
            return {"error": "Please answer with Yes or No."}

# Initialize bot handler
bot_handler = BotHandler()

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook endpoint for WhatsApp messages"""
    try:
        body = await request.json()
        
        # Extract message data
        if "entry" in body and body["entry"]:
            entry = body["entry"][0]
            if "changes" in entry and entry["changes"]:
                change = entry["changes"][0]
                if "value" in change and "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    
                    # Extract user phone and message text
                    user_mobile = message.get("from", "")
                    message_text = message.get("text", {}).get("body", "")
                    
                    # Process message
                    result = bot_handler.process_message(user_mobile, message_text)
                    
                    # Send response back to WhatsApp
                    if "message" in result:
                        # In a real implementation, you would send this back to WhatsApp API
                        return JSONResponse(content={"status": "success", "response": result["message"]})
                    elif "error" in result:
                        return JSONResponse(content={"status": "error", "response": result["error"]})
        
        return JSONResponse(content={"status": "success", "message": "Webhook received"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "FASTag WhatsApp/Interakt Backend is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
